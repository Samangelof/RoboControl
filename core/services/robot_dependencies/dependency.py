# RoboControl\services\dependency.py
import psutil


def check_ncalayer_running():
    """Проверка, запущен ли процесс NCALayer."""
    for proc in psutil.process_iter(['name']):
        try:
            if 'NCALayer' in proc.info['name']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False