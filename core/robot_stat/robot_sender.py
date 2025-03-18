import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from settings.logger import setup_logger


load_dotenv()
logger = setup_logger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID_STAT")
JSON_FILE = "reports.json"

def format_data(data):
    """
    Форматирует JSON-данные в читаемое сообщение, поддерживает списки и словари.
    """
    message_lines = ["Данные:"]
    
    if isinstance(data, list):  # Если JSON - список
        for index, item in enumerate(data, start=1):
            if isinstance(item, dict):  # Если элемент списка - словарь
                message_lines.append(f"\n")
                for key, value in item.items():
                    message_lines.append(f"{key}: {value}")
            else:  # Если обычное значение (например, просто список строк или чисел)
                message_lines.append(f"{index}. {item}")
    
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
        await bot.send_message(CHAT_ID, message)
        logger.info("[SEND SUCCESS] Отчёты отправлены успешно")

    except Exception as e:
        logger.info(f"[SEND ERROR] Ошибка при отправке: {e}")

    finally:
        # Закрываем сессию бота
        await bot.session.close()


# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(send_data())
