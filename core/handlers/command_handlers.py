from aiogram.types import Message
from aiogram.filters import Command
from core.loader import dp


@dp.message(Command('start'))
async def get_start(message: Message):
    await message.reply(f"Привет, {message.from_user.full_name}!")
    await message.answer("Я могу быть Вашим личным диетологом!")
    await message.answer("Чтобы узнать, что я умею делать - напишите /help")


@dp.message(Command('help'))
async def get_help(message: Message):
    await message.reply("Вот что я умею:")
    await message.answer("Если Вы отправите мне фото с едой - я могу определить ее БЖУ")
    await message.answer(
        "Если Вы отправите мне фото с этикеткой продукта - я могу распознать вредные ингредиенты на ней")
    await message.answer("Вы также можете добавить описание к фото - тогда я выполню задание из этого описания")
    await message.answer(
        "Если же Вы отправите мне голосовое сообщение с вашими продуктами - я могу подсказать, что из этого можно приготовить")
