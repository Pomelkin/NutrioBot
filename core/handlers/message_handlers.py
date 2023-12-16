import logging
import os

from aiogram import F, Bot
from aiogram.types import Message, FSInputFile
from core.API.OpenAI import preprosess_image, get_response_from_nutritionist, get_recipe_from_nutritionist
from core.loader import dp
from core.utils.placeholders import Placeholder
import io
import random
import string
import threading

from core.utils.utils import remove_file


# @dp.message(F.content_type.func(lambda content_type: content_type != 'text'))
# async def check_video(message: Message):
#     await message.answer(f'Извините, {message.from_user.full_name}. Я умею работать только с сообщениями.')


@dp.message(F.photo)
async def get_nutrio_recommendation(message: Message, bot: Bot):
    logging.info(f'start working with {message.from_user.full_name}')

    async with Placeholder(bot, message.chat.id):
        user_prompt = message.caption if message.caption is not None else ""

        stream_photo = await bot.download(message.photo[-1])
        base64_image = await preprosess_image(stream_photo)
        response = await get_response_from_nutritionist(base64_image, user_prompt)

    await message.reply(response, parse_mode='markdown')

    logging.info(f'stop working with {message.from_user.full_name}')


@dp.message(F.voice)
async def get_recipe(message: Message, bot: Bot):
    logging.info(f'start working with {message.from_user.full_name}')

    async with Placeholder(bot, message.chat.id):
        filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        speech_file_path = "temp/" + filename + ".mp3"
        await bot.download(message.voice, speech_file_path)

        file_path = await get_recipe_from_nutritionist(speech_file_path)

        if file_path != '':
            audio = FSInputFile(file_path)
            await message.reply_voice(audio)
            threading.Thread(target=remove_file, args=[file_path]).start()
        else:
            await message.answer("Что-то пошло не по плану...\n_Попробуйте еще раз_ !", parse_mode='markdown')

    threading.Thread(target=remove_file, args=[speech_file_path]).start()
    logging.info(f'stop working with {message.from_user.full_name}')

# @dp.callback_query(F.data == 'translate')
# async def translate(callback: CallbackQuery):
#     text = callback.message.text
#     translated_text_eu = GoogleTranslator(source='auto', target='english').translate(text=text)
#     await update_text(callback.message, translated_text_eu)
#     await callback.answer()
