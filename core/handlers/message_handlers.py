from aiogram import F, Bot
from aiogram.types import Message, VideoNote, CallbackQuery
from core.loader import dp
from core.utils import get_keyboard, update_text, get_info, get_letter
from core.placeholders import Placeholder
# from deep_translator import GoogleTranslator
import os
import asyncio
import requests
import json


@dp.message(F.content_type.func(lambda content_type: content_type != 'text'))
async def check_video(message: Message):
    await message.answer(f'Извините, {message.from_user.full_name}. Я умею работать только с сообщениями.')


@dp.message(F.text)
async def extract_url(message: Message, bot: Bot):
    async with Placeholder(bot, message.chat.id):
        try:
            url = ''
            entities = message.entities
            for entity in entities:
                if entity.type == 'url':
                    url = entity.extract_from(message.text)
        except Exception as e:
            print(e)
            url = ''

        if len(url) > 0:
            try:
                personal_letter = await get_letter(url)
                await message.reply(personal_letter)
            except Exception as e:
                print(e)
                await message.reply(f'Извините, {message.from_user.full_name}.\nЧто-то пошло не так, попробуйте снова ☹')
        else:
            await message.reply(f'Извините, {message.from_user.full_name}.\nЯ не смог найти ссылку в вашем сообщении ☹')

# @dp.callback_query(F.data == 'translate')
# async def translate(callback: CallbackQuery):
#     text = callback.message.text
#     translated_text_eu = GoogleTranslator(source='auto', target='english').translate(text=text)
#     await update_text(callback.message, translated_text_eu)
#     await callback.answer()
