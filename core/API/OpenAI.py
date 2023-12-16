from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY
import cv2
import base64
import io
import numpy as np
import json
import logging
import random
import string


async def preprosess_image(img_stream):
    file_bytes = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    new_shape0 = 1200 if img.shape[1] >= 1200 else img.shape[1]
    new_shape1 = 768 if img.shape[0] >= 768 else img.shape[0]
    img = cv2.resize(img, (new_shape0, new_shape1))

    _, img_encode = cv2.imencode('.jpg', img)
    b64encoded_image = base64.b64encode(img_encode).decode('utf-8')
    return b64encoded_image


async def get_response_from_nutritionist(base64_image, prompt):
    try:
        is_prompt_from_user = False
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)

        role_vision_model = """
        You are a personal nutritionist that help determining how many proteins, fats and carbohydrates are in the dish
        or recognize harmful ingredients on the product label and gives recommendations about nutrition.
        """

        if not (prompt == ""):
            is_prompt_from_user = True
        else:
            prompt = """
            If you see product label -
            recognize harmful ingredients on the label,
            else if you see dish on the picture -
            tell How many proteins, fats and carbohydrates are in the dish in the picture, just think about it and reason
            """

        response = await client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": role_vision_model,
                },
                {
                    "role": "user",
                    "content":
                        [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpg;base64,{base64_image}",
                                    "detail": "high"
                                },
                            },
                        ],
                }
            ],
            max_tokens=1024,
        )

        response_vision = response.choices[0].message.content

        if is_prompt_from_user:
            logging.info('nutritionist_answer: ready')
            return response_vision

        role_assistant = """
        You are a nutritionists assistant who helps determining how many proteins, fats and carbohydrates are in the dish
        or recognize harmful ingredients on the product label.
        You designed to output JSON.
        JSON looks like {
          "product_label": {
            "found": 1 - for true or 0 - for false
            "name":
            "harmful_ingredients": here you need to write about a harmful ingredient ,
            }
          "dish": {
            "found": 1 - for true or 0 - for false
            "name":
            "proteins": {"per_100g": here only integers},
            "fats": {"per_100g": here only integers},
            "carbohydrates": {"per_100g": here only integers}
          }
          "recommendation": as a nutritionist
        }
        if dont see anything about the dish - use none value,the same for the product label
        Use Russian in your answers, because you customers are only russians
        """

        response = await client.chat.completions.create(
            model="gpt-4-1106-preview",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": role_assistant
                },
                {
                    "role": "user",
                    "content":
                        f"""
              You need to process the response from the another model and give a JSON. The response: {response_vision}.
              """
                }
            ],
        )
        response_assistant = response.choices[0].message.content

    except Exception as e:
        logging.error(e)
        return "Произошла ошибка доступа к серверу OpenAI, попробуйте позже"

    nutritionist_answer = ""
    try:
        response = json.loads(response_assistant)

        if response['product_label']['found']:
            nutritionist_answer = \
                f"*Этикетка продукта* : {response['product_label']['name'] if response['product_label']['name'] != 'none' else 'Не удалось распознать!'}\n\n" + \
                f"*Вредные ингридиенты* : {response['product_label']['harmful_ingredients'] if response['product_label']['harmful_ingredients'] != 'none' else 'Не удалось распознать!'}\n\n" + \
                f"*Рекомендация* : {response['recommendation'] if response['recommendation'] != 'none' else 'Не удалось распознать!'}"
        elif response['dish']['found']:
            nutritionist_answer = \
                f"*Блюдо* : {response['dish']['name'] if response['dish']['name'] != 'none' else 'Не удалось распознать!'}\n\n" \
                f"*БЖУ на 100г. продукта* :\n" + \
                f"- _Белки_ : {str(response['dish']['proteins']['per_100g']) + 'г.' if response['dish']['proteins']['per_100g'] != 'none' else 'Не удалось распознать!'}\n" + \
                f"- _Жиры_ : {str(response['dish']['fats']['per_100g']) + 'г.' if response['dish']['fats']['per_100g'] != 'none' else 'Не удалось распознать!'}\n" + \
                f"- _Углеводы_ : {str(response['dish']['carbohydrates']['per_100g']) + 'г.' if response['dish']['carbohydrates']['per_100g'] != 'none' else 'Не удалось распознать!'}\n\n" + \
                f"*Рекомендация* : {response['recommendation'] if response['recommendation'] != 'none' else 'Не удалось распознать!'}"
        else:
            nutritionist_answer = "Хммм, я не смог увидеть этикетку продукта или блюдо.\n_Попробуйте еще раз_ !"

    except Exception as e:
        logging.error(e)
        nutritionist_answer = "Что-то пошло не по плану...\n_Попробуйте еще раз_ !"

    return nutritionist_answer


async def get_recipe_from_nutritionist(audio_path):
    try:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)

        audio_file = open(audio_path, "rb")
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            prompt="You need to transcript a products from the speech",
            response_format="text"
        )

        role_assistant = """
        You are a nutritionist who analyzes transcriptions from the client's speech and helps to prepare a healthy lifestyle dish from the client's products. In your answers use the language that is in the transcription
        """

        response = await client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "system",
                    "content": role_assistant
                },
                {
                    "role": "user",
                    "content":
                        f"""
              You need to process the response from the whisper model. The response: {transcript}. In your recipe you can use not all client's products. In your answer use the language that is in the transcription
              """
                }
            ],
        )

        response_assistant = response.choices[0].message.content
        filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        speech_file_path = "temp/" + filename + ".mp3"
        response = await client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=response_assistant
        )
        await response.astream_to_file(speech_file_path)
        return speech_file_path

    except Exception as e:
        logging.error(e)
        return ""
