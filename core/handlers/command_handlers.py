from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F
from core.loader import dp


@dp.message(F.text, Command('start'))
async def get_start(message: Message):
    await message.reply(f"Привет, {message.from_user.full_name}!")
    await message.answer("Я умею делать персонализированные предложения для клиента по ссылке на профиль Linkedin.")
    await message.answer("Попробуйте отправить мне сообщение с ссылкой.\nНе бойтесь, строго формата сообщения нет, я умею извлекать ссылки из текста 😄")
    await message.answer('Пример корректной ссылки:\nhttps://www.linkedin.com/in/{имя_пользователя}/')