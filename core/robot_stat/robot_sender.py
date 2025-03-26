import os
import json
import asyncio
import re
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from settings.logger import setup_logger
import datetime


load_dotenv()
logger = setup_logger(__name__)
current_date = datetime.date.today().isoformat()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID_STAT")
JSON_FILE = "reports.json"

def extract_company_name(full_name):
    """
    Извлекает название компании, заключенное в кавычки.
    """
    match = re.search(r'"(.+)', full_name)  # Находит текст внутри кавычек
    return match.group(1) if match else full_name  # Возвращает текст внутри кавычек, иначе оригинальное название

def format_data(data):
    """
    Форматирует JSON-данные в читаемое HTML-сообщение для Telegram.
    """
    message_lines = [f"<b>📊 Отчёты {current_date}:</b>"]

    if isinstance(data, list):  # Если JSON - список записей
        for index, item in enumerate(data, start=1):
            if isinstance(item, dict):  # Если элемент списка - словарь
                message_lines.append(f"\n<b>📌 Отчёт №{index}:</b>")  # 🔹 Теперь это "Отчёт"
                for key, value in item.items():
                    # Если это название компании, применяем обработку
                    if key.lower() == "название компании":
                        value = extract_company_name(value)
                    message_lines.append(f"🔹 <b>{key}:</b> {value}")
    
    else:
        message_lines.append(str(data))  # Просто строка или число

    return "\n".join(message_lines)

async def send_data():
    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    # Читаем JSON
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Формируем сообщение
        message = format_data(data)

        # Отправляем сообщение в чат
        await bot.send_message(CHAT_ID, message, parse_mode="HTML")
        logger.info("[SEND SUCCESS] Отчёты отправлены успешно")

    except Exception as e:
        logger.info(f"[SEND ERROR] Ошибка при отправке: {e}")

    finally:
        # Закрываем сессию бота
        await bot.session.close()


# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(send_data())
