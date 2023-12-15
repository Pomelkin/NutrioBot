from aiogram import Bot, Dispatcher
from core.config import TELEGRAM_TOKEN, MODE, WEBHOOK_URL, PORT
from core.handlers.command_handlers import *
from core.handlers.message_handlers import *
from core.loader import dp, bot
import asyncio
import logging

TELEGRAM_API_KEY = TELEGRAM_TOKEN


async def on_startup(dp):
    if MODE == "webhook":
        await bot.set_webhook(WEBHOOK_URL + '/' + TELEGRAM_TOKEN)
        logging.info(f"Start webhook mode on port {PORT}")
    else:
        logging.info(f"Start polling mode")


async def start_bot():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')

    try:
        await dp.start_polling(bot, on_startup=on_startup, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start_bot())
