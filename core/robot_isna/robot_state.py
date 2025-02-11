# state.py
from enum import Enum


class RobotState(Enum):
    NOT_STARTED = "Not Started"
    NAVIGATION_STARTED = "Navigation Started"
    NAVIGATION_COMPLETED = "Navigation Completed"
    AUTH_STARTED = "Authentication Started"
    AUTH_COMPLETED = "Authentication Completed"
    ERROR = "Error"