from aiogram import Bot


class Placeholder:
    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id
        self.message = None

    async def __aenter__(self):
        self.message = await self.bot.send_message(self.chat_id, "🤖 _Обработка..._", parse_mode="markdown")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.bot.delete_message(self.chat_id, self.message.message_id)
