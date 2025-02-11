# services/tracker.py
from datetime import datetime
from core.services.utils.json_storage import save_run_data
from settings.system_info import system_information
from settings.logger import setup_logger


logger = setup_logger(__name__)


def start_robot_with_logging(robot, selected_path: str):
    """Логирование времени начала и окончания работы робота"""
    #* <<< --- Сохранить в логи системные настройки -- >>>
    # system_information()
    start_time = datetime.now()
    run_data = {
        "run_id": start_time.isoformat(),
        "start_time": start_time.isoformat(),
        "parameters": {"path": selected_path},
        "status": "failure",
    }

    try:
        # Логируем успешное начало
        logger.info("[START LOGGING] Начало работы робота.")
        return run_data
    except Exception as e:
        run_data["error_message"] = str(e)
        save_run_data(run_data)
        raise
