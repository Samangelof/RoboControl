from aiogram import Bot, Dispatcher
from aiogram.utils import executor
import os
import pathlib
import asyncio
from aiogram.types import InputMediaDocument



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def log_message(message, is_error=False):
    """Унифицированное логирование"""
    prefix = "[ERROR TELEGRAM BOT]" if is_error else "[TELEGRAM BOT]"
    full_message = f"{prefix} {message}"
    spectator_logging(full_message)
    print(full_message)

async def remove_file(file_path):
    """Асинхронное удаление файла"""
    try:
        os.remove(file_path)
    except Exception as e:
        await log_message(f"Ошибка при удалении файла {file_path}: {e}", is_error=True)

async def send_excel_file(dispatcher):
    excel_file_path = pathlib.Path.cwd() / 'result.xlsx'

    if not excel_file_path.exists():
        await log_message("Excel файл не существует, данных для отправки нет")
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
    pdf_folder = pathlib.Path.cwd() / 'data'

    if not pdf_folder.exists():
        await log_message("Директория не существует, данных для отправки нет")
        return False

    files = [pdf_folder / file_name for file_name in os.listdir(pdf_folder) if (pdf_folder / file_name).is_file()]
    if not files:
        await log_message("Нет файлов для отправки в директории")
        return False

    chunk_size = 10
    file_chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]
    
    file_handles = []  # Для отслеживания открытых файлов

    try:
        for chunk in file_chunks:
            if len(chunk) == 1:
                file_path = chunk[0]
                file_handle = open(file_path, 'rb')
                file_handles.append(file_handle)
                
                await dispatcher.bot.send_document(
                    chat_id=CHAT_ID, 
                    document=file_handle, 
                    caption=user_info
                )
                await log_message(f"Файл {file_path.name} отправлен")
            else:
                media = []
                for index, file_path in enumerate(chunk):
                    file_handle = open(file_path, 'rb')
                    file_handles.append(file_handle)
                    
                    caption = user_info if index == len(chunk) - 1 else ""
                    media.append(InputMediaDocument(
                        media=file_handle, 
                        caption=caption
                    ))

                await dispatcher.bot.send_media_group(chat_id=CHAT_ID, media=media)
                await log_message(f"Медиагруппа из {len(media)} файлов отправлена")
                await asyncio.sleep(2)  # Защита от флуда

        return True
    except Exception as e:
        await log_message(f"Ошибка при отправке файлов: {e}", is_error=True)
        return False
    finally:
        # Закрыть все открытые файловые дескрипторы
        for handle in file_handles:
            handle.close()
        
        # Удалить файлы после отправки
        for file_path in files:
            await remove_file(file_path)
        
        await log_message("Операция завершена, все файлы обработаны")

if __name__ == '__main__':
    # Разные варианты запуска
    # executor.start_polling(dp, on_startup=send_excel_file)
    executor.start_polling(dp, on_startup=lambda dp: send_files(dp, "Пакет файлов"))