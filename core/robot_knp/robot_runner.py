# core/robot_runner.py
import time
from datetime import datetime
from core.robot_knp.robot_manager import RobotKNP
from core.services.robot_dependencies.dependency import check_ncalayer_running
from core.services.tracking.tracker import start_robot_with_logging
from core.services.utils.json_storage import save_run_data
from settings.logger import setup_logger


logger = setup_logger(__name__)


def start_robot_service_knp(robot: RobotKNP, selected_path: str) -> bool:
    """Логика запуска для RobotKNP."""
    if not check_ncalayer_running():
        logger.error("[NCALayer not found] Процесс NCALayer не найден")
        return False

    try:
        # lOGGING START LAUNCH ROBOT
        run_data = start_robot_with_logging(robot, selected_path)

        # [START]
        robot.navigation_proccess()
        logger.info("[NAVIGATION SUCCESS] Навигация началась успешно")
        run_data["navigation_status"] = "success"

        # [AUTH]
        robot.authenticate_proccess(selected_path)
        logger.info("[AUTHENTICATE SUCCESS] Аутентификация прошла успешно")
        run_data["authentication_status"] = "success"

        # [BALANCE]
        robot.balance_personal_accounts()
        logger.info("[BALANCE SUCCESS] Проверка сальдо прошла успешно")
        
        # [END]
        run_data["status"] = "success"
        logger.info("[GGWP] Робот успешно завершил все этапы запуска")

        # SAVE LAUNCH DATA
        end_time = datetime.now()
        run_data["end_time"] = end_time.isoformat()
        run_data["duration"] = (end_time - datetime.fromisoformat(run_data["start_time"])).total_seconds()
        save_run_data(run_data)

        return True
    except Exception as Err:
        logger.error(f"[ERROR RUN ROBOT (start_robot_service_knp)] Ошибка при запуске робота: {Err}")
        return False
