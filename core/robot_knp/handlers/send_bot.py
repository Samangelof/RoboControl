import os
import pathlib
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import InputMediaDocument
from settings.logger import setup_logger
from aiogram.utils import executor


CHAT_ID = os.getenv("TELEGRAM_CHAT_ID_KNP")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logger = setup_logger(__name__)


async def log_message(message, is_error=False):
    """Красивый лог"""
    prefix = "❌" if is_error else "✅"
    logger.info(f"{prefix} {message}")

async def remove_file(file_path):
    """Асинхронное удаление файла"""
    try:
        await asyncio.to_thread(os.remove, file_path)
    except Exception as e:
        await log_message(f"Ошибка при удалении файла {file_path}: {e}", is_error=True)

async def send_excel_file(dispatcher):
    """Отправка Excel-файла"""
    excel_file_path = pathlib.Path.cwd() / 'result.xlsx'

    if not excel_file_path.exists():
        await log_message("Excel файл не найден, отправка отменена")
        return False

    try:
        async with open(excel_file_path, 'rb') as file:
            await dispatcher.bot.send_document(chat_id=CHAT_ID, document=file)
        
        await remove_file(excel_file_path)
        await log_message("Excel файл отправлен и удалён")
        return True
    except Exception as e:
        await log_message(f"Ошибка при отправке Excel файла: {e}", is_error=True)
        return False

async def send_files(dispatcher, user_info=""):
    """Отправка всех файлов из папки data"""
    project_root = pathlib.Path.cwd()
    pdf_folder = project_root / "core" / "robot_knp" / "data"
    print(f"Проверяем путь: {pdf_folder}, существует: {pdf_folder.exists()}")

    if not pdf_folder.exists():
        await log_message("Директория не найдена, отправка отменена")
        return False

    files = [pdf_folder / file_name for file_name in os.listdir(pdf_folder) if (pdf_folder / file_name).is_file()]
    
    if not files:
        await log_message("Файлы для отправки не найдены")
        return False

    chunk_size = 10
    file_chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]
    success = True

    try:
        for chunk in file_chunks:
            if len(chunk) == 1:
                file_path = chunk[0]
                with open(file_path, 'rb') as file_handle:
                    await dispatcher.bot.send_document(
                        chat_id=CHAT_ID, 
                        document=file_handle, 
                        caption=user_info
                    )
                await log_message(f"Файл {file_path.name} отправлен")
            else:
                file_handles = []
                media = []
                
                try:
                    # Открытие всех файлов сразу
                    for index, file_path in enumerate(chunk):
                        file_handle = open(file_path, 'rb')
                        file_handles.append(file_handle)
                        
                        caption = user_info if index == len(chunk) - 1 else ""
                        media.append(InputMediaDocument(
                            media=file_handle,
                            caption=caption
                        ))

                    # Отправки группой
                    await dispatcher.bot.send_media_group(chat_id=CHAT_ID, media=media)
                    await log_message(f"Медиагруппа из {len(media)} файлов отправлена")
                finally:
                    # Закрыие всех файлов после отправки
                    for handle in file_handles:
                        handle.close()
                
                # Защита от флуда
                await asyncio.sleep(2)

    except Exception as e:
        await log_message(f"Ошибка при отправке файлов: {e}", is_error=True)
        success = False

    if success:
        for file_path in files:
            await remove_file(file_path)
        await log_message("Файлы успешно отправлены и удалены")

    return success


# if __name__ == '__main__':
    # Варианты запуска
    # executor.start_polling(dp, on_startup=send_excel_file)
    #! Передается описание файлов (userInfo)
    # executor.start_polling(dp, on_startup=lambda dp: send_files(dp, "Пакет файлов"))