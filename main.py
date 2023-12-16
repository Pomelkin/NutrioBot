from core.config import TELEGRAM_TOKEN, MODE, WEBHOOK_URL, PORT
from core.handlers.command_handlers import *
from core.handlers.message_handlers import *
import asyncio
import logging
from core.config import TELEGRAM_TOKEN
from core.loader import bot, dp
from core.utils.commands import set_commands

TELEGRAM_API_KEY = TELEGRAM_TOKEN


async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    if MODE == "webhook":
        await bot.set_webhook(WEBHOOK_URL + '/' + TELEGRAM_TOKEN)
        logging.info(f"Start webhook mode on port {PORT}")
    else:
        logging.info(f"Start polling mode")


async def start_bot():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
    try:
        await set_commands(bot)
        await dp.start_polling(bot, on_startup=on_startup)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start_bot())
