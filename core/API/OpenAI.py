from openai import AsyncOpenAI
from core.config import OPENAI_API_KEY
import cv2
import base64
import io
import numpy as np
import json
import logging


async def preprosess_image(img_stream):
    file_bytes = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    new_shape0 = 1200 if img.shape[1] >= 1200 else img.shape[1]
    new_shape1 = 768 if img.shape[0] >= 768 else img.shape[0]
    img = cv2.resize(img, (new_shape0, new_shape1))

    _, img_encode = cv2.imencode('.jpg', img)
    b64encoded_image = base64.b64encode(img_encode).decode('utf-8')
    return b64encoded_image


async def get_response_from_nutritionist(base64_image, prompt=""):
    prompt_from_user = False

    try:
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logging.error(e)
        return "Произошла ошибка доступа к серверу OpenAI, попробуйте позже"

    role_vision_model = """
    You are a personal nutritionist that help determining how many proteins, fats and carbohydrates are in the dish
    or recognize harmful ingredients on the product label and gives recommendations about nutrition.
    """

    if not (prompt == ""):
        prompt_from_user = True
    else:
        prompt = """
        If you see product label -
        recognize harmful ingredients on the label,
        else if you see dish on the picture -
        tell How many proteins, fats and carbohydrates are in the dish in the picture, just think about it and reason
        """

    try:
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
    except Exception as e:
        logging.error(e)
        return "Произошла ошибка доступа к серверу OpenAI, попробуйте позже"

    response_vision = response.choices[0].message.content
    print(response_vision)

    if prompt_from_user:
        return response_vision

    role_assistant = """
    You are a nutritionists assistant that help determining how many proteins, fats and carbohydrates are in the dish
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

    try:
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
    except Exception as e:
        logging.error(e)
        return "Произошла ошибка доступа к серверу OpenAI, попробуйте позже"

    response_assistant = response.choices[0].message.content
    print(response_assistant)

    nutritionist_answer = ""
    try:
        response = json.loads(response_assistant)

        if response['product_label']['found']:
            nutritionist_answer = f"""
          **Этикетка продукта** : {response['product_label']["name"] if response['product_label']["name"] != 'none' else 'Не удалось распознать!'}\n
          **Вредные ингридиенты** : {response['product_label']["harmful_ingredients"] if response['product_label']["harmful_ingredients"] != 'none' else 'Не удалось распознать!'}\n\n
    
          **Рекомендация** : {response["recommendation"] if response["recommendation"] != 'none' else 'Не удалось распознать!'}
          """
        else:
            nutritionist_answer = f"""
          **Блюдо** : {response['dish']["name"] if response['dish']["name"] != 'none' else 'Не удалось распознать!'}\n
          **БЖУ на 100г. продукта** :
          - *Белки* : {str(response['dish']["proteins"]['per_100g']) + 'г.' if response['dish']["proteins"]['per_100g'] != 'none' else 'Не удалось распознать!'}
          - *Жиры* : {str(response['dish']["fats"]['per_100g']) + 'г.' if response['dish']["fats"]['per_100g'] != 'none' else 'Не удалось распознать!'}
          - *Углеводы* : {str(response['dish']['carbohydrates']['per_100g']) + 'г.' if response['dish']['carbohydrates']['per_100g'] != 'none' else 'Не удалось распознать!'}\n
    
          Рекомендация: {response["recommendation"] if response["recommendation"] != 'none' else 'Не удалось распознать!'}
          """
    except Exception as e:
        logging.error(e)
        nutritionist_answer = "Не удалось распознать, попробуйте еще раз."

    print(nutritionist_answer)
    return nutritionist_answer
