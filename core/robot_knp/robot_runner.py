# core/robot_runner.py
import time
from datetime import datetime
import asyncio
from core.robot_knp.robot_manager import RobotKNP
from core.services.robot_dependencies.dependency import check_ncalayer_running
from core.services.tracking.tracker import start_robot_with_logging
from core.services.utils.json_storage import save_run_data
from core.robot_knp.handlers.send_bot import executor, dp, send_files
from settings.logger import setup_logger


logger = setup_logger(__name__)


def start_robot_service_knp(robot: RobotKNP, selected_path: str) -> tuple[bool, str]:
    """Логика запуска для RobotKNP."""
    if not check_ncalayer_running():
        logger.error("[NCALayer not found] Процесс NCALayer не найден")
        return False

    try:
        # [WRITE LOGGING] lOGGING START LAUNCH ROBOT
        run_data = start_robot_with_logging(robot, selected_path)

        # [START]
        robot.navigation_proccess()
        logger.info("[NAVIGATION SUCCESS] Навигация началась успешно")
        run_data["navigation_status"] = "success"

        # [AUTH]
        auth_result = robot.authenticate_proccess(selected_path)
        if not auth_result:
            logger.warning("[AUTHENTICATE FAIL] Авторизация не пройдена, процесс завершен")
            run_data["authentication_status"] = "auth_failed"
            return True
        
        logger.info("[AUTHENTICATE SUCCESS] Аутентификация прошла успешно")
        run_data["authentication_status"] = "success"

        # [BALANCE]
        # logger.info("[BALANCE SUCCESS] Проверка сальдо началась успешно")
        # robot.balance_personal_accounts()
        # logger.info("[BALANCE SUCCESS] Проверка сальдо прошла успешно")
        
        # [DOCUMENTS]
        logger.info("[DOCUMENTS START] Процесс с документами начался успешно")
        robot.process_documents()
        run_data["process_documents"] = "success"
        logger.info("[DOCUMENTS SUCCESS] Процесс с документами прошел успешно")
        
        # [END]
        logger.info("[EXIT START] Начался процесс выхода из системы")
        robot.exit()
        logger.info("[EXIT SUCCESS] Процесс с документами прошел успешно")
        run_data["status"] = "success"
        logger.info("[SEND FILES TG START] Отправляю все файлы в тг")

        # SEND DOCS 
        try:
            asyncio.run(send_files(dp, "Пакет файлов"))
            logger.info("[SEND FILES TG SUCCESS] Все файлы успешно отправлены в тг")
        except Exception as e:
            logger.error(f"[SEND FILES TG ERROR] Ошибка при отправке файлов: {e}")

        logger.info("[GGWP] Робот успешно завершил все этапы!")


        # SAVE LAUNCH DATA
        end_time = datetime.now()
        run_data["end_time"] = end_time.isoformat()
        run_data["duration"] = (end_time - datetime.fromisoformat(run_data["start_time"])).total_seconds()
        save_run_data(run_data)

        return True
    except Exception as Err:
        logger.error(f"[ERROR RUN ROBOT (start_robot_service_knp)] Ошибка при запуске робота: {Err}")
        run_data["status"] = "FATAL_RUN_ROBOT"
        return False
