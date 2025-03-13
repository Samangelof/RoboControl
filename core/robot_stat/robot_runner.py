# core/robot_stat/robot_runner.py
import time
from datetime import datetime
from core.robot_stat.robot_manager import RobotStat
from core.services.robot_dependencies.dependency import check_ncalayer_running
from core.services.tracking.tracker import start_robot_with_logging
from core.services.utils.json_storage import save_run_data
from settings.logger import setup_logger


logger = setup_logger(__name__)


def start_robot_service_stat(robot: RobotStat, selected_path: str) -> bool:
    """Проверка, запущен ли процесс NCALayer, и запуск робота"""    
    try:
        # [CHECK]
        robot.check_certificates(selected_path)
        # [START]
        logger.info("[NAVIGATION SUCCESS] Навигация началась успешно")
        robot.navigation_proccess()
        logger.info("[NAVIGATION SUCCESS] Навигация завершена успешно")

        # [AUTH]
        logger.info("[AUTH SUCCESS] Авторизация началась успешно")
        robot.authenticate_proccess(selected_path)
        logger.info("[AUTH SUCCESS] Авторизация завершена успешно")
        # logger.info("[REPORTS SUCCESS] Отчеты собраны началась успешно")
        # robot.reports_proccess()
        # logger.info("[REPORTS SUCCESS] Отчеты собраны завершена успешно")


        # [END]
        logger.info("[GGWP] Робот успешно завершил все этапы запуска")

        return True
    except Exception as Err:
        logger.error(f"[ERROR RUN ROBOT (start_robot_service_stat)] Ошибка при запуске робота: {Err}")
        return False
