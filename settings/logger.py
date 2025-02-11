import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    if 'robot_isna' in name:
        robot_type = 'robot_isna'
    elif 'robot_stat' in name:
        robot_type = 'robot_stat'
    elif 'robot_knp' in name:
        robot_type = 'robot_knp'
    else:
        robot_type = 'general'

    log_dir = os.path.join('logs', robot_type)
    os.makedirs(log_dir, exist_ok=True)

    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'Robot_{current_date}.log')

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)


    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger





# logger = setup_logger(__name__)
