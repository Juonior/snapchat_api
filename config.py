from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()


# Получение значений переменных окружения
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY')
CHATGPT_BASE_PROPMT = os.getenv('CHATGPT_BASE_PROPMT')
PROXY_URL = os.getenv('PROXY_URL')
