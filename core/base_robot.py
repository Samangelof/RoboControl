# core/base_robot.py
from abc import ABC, abstractmethod
import logging
# from core.services.utils.common import RobotState
from core.services.robot_dependencies.selenium_driver import SeleniumDriver


class BaseRobot(ABC):
    def __init__(self, save_path: str = None):
        self.driver = SeleniumDriver(save_path=save_path)
        # self.state = RobotState.NOT_STARTED

    @abstractmethod
    def navigation_proccess(self):
        """Начать навигацию. Должен быть реализован в каждом роботе"""
        pass

    @abstractmethod
    def authenticate_proccess(self, selected_path):
        """Выполнить авторизацию. Должен быть реализован в каждом роботе"""
        pass