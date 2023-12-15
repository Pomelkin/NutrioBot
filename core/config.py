from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
PROXYCURL_API_KEY = os.environ.get("PROXYCURL_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PORT = int(os.environ.get("PORT", 5000))
MODE = os.environ.get("MODE", "webhook")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")