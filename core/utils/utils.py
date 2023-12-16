from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import os


def get_keyboard(text, callback_data):
    buttons = [
        [InlineKeyboardButton(text=text, callback_data=callback_data)],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def update_text(message: Message, new_value: str):
    with suppress(TelegramBadRequest):
        await message.edit_text(new_value)


def remove_file(path):
    os.remove(path)
    return
