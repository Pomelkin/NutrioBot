from aiogram import F, Bot
from aiogram.types import Message
from core.API.OpenAI import preprosess_image, get_response_from_nutritionist
from core.loader import dp
from core.utils.placeholders import Placeholder
import io

# @dp.message(F.content_type.func(lambda content_type: content_type != 'text'))
# async def check_video(message: Message):
#     await message.answer(f'Извините, {message.from_user.full_name}. Я умею работать только с сообщениями.')


@dp.message(F.photo)
async def get_nutrio_recommendation(message: Message, bot: Bot):
    async with Placeholder(bot, message.chat.id):
        stream_photo = await bot.download(message.photo[-1].file_id)
        base64_image = await preprosess_image(stream_photo)
        response = await get_response_from_nutritionist(base64_image)

    await message.answer(response)



# @dp.callback_query(F.data == 'translate')
# async def translate(callback: CallbackQuery):
#     text = callback.message.text
#     translated_text_eu = GoogleTranslator(source='auto', target='english').translate(text=text)
#     await update_text(callback.message, translated_text_eu)
#     await callback.answer()
