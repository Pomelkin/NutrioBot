from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F
from core.loader import dp


@dp.message(F.text, Command('start'))
async def get_start(message: Message):
    await message.reply(f"Привет, {message.from_user.full_name}!")
    await message.answer("Я могу быть твоим личным нутрициологом")