import customtkinter
import os
import requests
import winsound
from PIL import Image
from customtkinter import filedialog
from core.services.utils.json_storage import save_path_to_json, load_config
from core.services.robot_dependencies.dependency import check_ncalayer_running
from core.robot_isna.robot_runner import start_robot_service_isna
from core.robot_knp.robot_runner import start_robot_service_knp
from core.robot_stat.robot_runner import start_robot_service_stat
from dotenv import load_dotenv, set_key
from settings.logger import setup_logger

from core.robot_isna.robot_manager import RobotISNA
from core.robot_knp.robot_manager import RobotKNP
from core.robot_stat.robot_manager import RobotStat




load_dotenv()


logger = setup_logger(__name__)


class GuiRoboControl(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.robot_isna = RobotISNA()
        self.robot_knp = RobotKNP()
        self.robot_stat = RobotStat()


        self.title("RoboController")
        self.geometry("700x450")
        # ==================================================================================================================================
        # path
        self.selected_path = load_config()
        # ==================================================================================================================================

        # Настройка сетки для размещения виджетов
        self.grid_rowconfigure(0, weight=1)  # Одна строка с равным распределением
        self.grid_columnconfigure(1, weight=1)  # Вторая колонка (главная область)
        
        self.env_file = ".env" 

        # Загрузка изображений (поддержка светлого и тёмного режимов)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # Корневая директория проекта
        image_path = os.path.join(BASE_DIR, "resources", "images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")), size=(500, 150))
        self.icon_run = customtkinter.CTkImage(Image.open(os.path.join(image_path, "run.png")), size=(30, 30))
        self.icon_select_path = customtkinter.CTkImage(Image.open(os.path.join(image_path, "select_path.png")), size=(30, 30))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # Создание панели навигации
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # Лейбл с логотипом на панели навигации
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  RoboControl", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Кнопки на панели навигации
        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Главная",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Настройки",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Frame 3",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        # Выпадающее меню для смены темы
        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Главная страница
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        # Элементы главной страницы
        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)
        
        # ==================================================================================================================================
        # Кнопка "Run"
        self.button_run = customtkinter.CTkButton(
            self.home_frame, 
            text="ЖМИ СЮДА", 
            image=self.icon_run, 
            height=50,
            width=200,
            cursor="hand2",
            command=self.check_and_start_robot
        )
        self.button_run.grid(row=1, column=0, padx=20, pady=10)

        # ==================================================================================================================================
        # Кнопка "Указать путь"
        self.button_select_path = customtkinter.CTkButton(
            self.home_frame, 
            text="",
            image=self.icon_select_path,
            height=50, 
            width=200, 
            cursor="hand2", 
            command=self.select_path
        )
        self.button_select_path.grid(row=2, column=0, padx=20, pady=10)

        # ==================================================================================================================================
        # Метка для отображения выбранного пути
        self.path_label = customtkinter.CTkLabel(self.home_frame, text="~~ Выбранный путь будет отображен здесь ~~")
        self.path_label.grid(row=3, column=0, padx=20, pady=10)

        
        # Если путь найден, обновляем текст метки
        if self.selected_path:
            self.path_label.configure(text=self.selected_path)

            
        # ==================================================================================================================================
        # Вторая страница с тумблерами
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_columnconfigure(0, weight=1)
        
        # Добавляем заголовок для тумблеров
        self.toggles_label = customtkinter.CTkLabel(
            self.second_frame,
            text="Настройки робота",
            font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.toggles_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Тумблер ИСНА
        self.toggle_isna = customtkinter.CTkSwitch(
            self.second_frame,
            text="ИСНА",
            command=self.toggle_isna_event,
            onvalue=True,
            offvalue=False
        )
        # Устанавливаем начальное состояние из .env
        self.toggle_isna.select() if os.getenv("ENABLE_ISNA", "false").lower() == "true" else self.toggle_isna.deselect()
        self.toggle_isna.grid(row=1, column=0, padx=40, pady=(20, 10))
        
        # Тумблер КНП
        self.toggle_knp = customtkinter.CTkSwitch(
            self.second_frame,
            text="КНП",
            command=self.toggle_knp_event,
            onvalue=True,
            offvalue=False
        )
        # Устанавливаем начальное состояние из .env
        self.toggle_knp.select() if os.getenv("ENABLE_KNP", "false").lower() == "true" else self.toggle_knp.deselect()
        self.toggle_knp.grid(row=3, column=0, padx=20, pady=10)

        # Тумблер СТАТ
        self.toggle_stat = customtkinter.CTkSwitch(
            self.second_frame,
            text="СТАТ",
            command=self.toggle_stat_event,
            onvalue=True,
            offvalue=False
        )
        # Устанавливаем начальное состояние из .env
        self.toggle_stat.select() if os.getenv("ENABLE_STAT", "false").lower() == "true" else self.toggle_stat.deselect()
        self.toggle_stat.grid(row=2, column=0, padx=20, pady=10)

        # Третья страница
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # По умолчанию показываем главную страницу
        self.select_frame_by_name("home")

    def update_env_variable(self, key: str, value: bool):
        """Обновляет переменную окружения в файле .env"""
        try:
            # Преобразуем булево значение в строку для .env файла
            value_str = str(value).lower()
            # Обновляем переменную в .env файле
            set_key(self.env_file, key, value_str)
            # Обновляем переменную в текущем окружении
            os.environ[key] = value_str
            logger.info(f'Переменная {key} установлена в значение {value_str}')
        except Exception as e:
            logger.error(f'Ошибка при обновлении переменной {key}: {str(e)}')
            self.show_error_message(f"Ошибка при обновлении настроек: {str(e)}")

    def toggle_isna_event(self):
        """Обработчик события для тумблера ИСНА"""
        state = self.toggle_isna.get()
        self.update_env_variable("ENABLE_ISNA", state)
    
    def toggle_knp_event(self):
        """Обработчик события для тумблера ИСНА"""
        state = self.toggle_knp.get()
        self.update_env_variable("ENABLE_KNP", state)

    def toggle_stat_event(self):
        """Обработчик события для тумблера СТАТ"""
        state = self.toggle_stat.get()
        self.update_env_variable("ENABLE_STAT", state)

    def check_internet_connection(self):
        """Проверка подключения к интернету."""
        try:
            response = requests.get("https://www.google.com", timeout=5)
            logger.info(f'{response.status_code}')
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    #* если появится новый робот, достаточно будет написать для него свою start_robot_service и передать ее в run_robot
    def run_robot(self, robot_type: str, robot_instance, start_robot_service, enabled: bool) -> bool:
        """
        Запуск отдельного робота с обработкой ошибок
        
        Args:
            robot_type: Тип робота ("ИСНА" или "СТАТ")
            robot_instance: Экземпляр робота (self.robot_isna или self.robot_stat)
            start_robot_service (Callable[[Any, str], bool]): Функция, отвечающая за запуск робота. 
                Принимает два аргумента:
                    - robot_instance: Экземпляр робота.
                    - selected_path: Путь, переданный для выполнения задачи.
                Возвращает bool: True, если робот успешно выполнил задачу, иначе False.
            enabled (bool): Флаг включения робота. Если False, робот не будет запущен.

        Returns:
            bool: True, если робот успешно выполнил работу, иначе False.
        """
        if not enabled:
            return False
            
        logger.info(f"Запуск робота {robot_type}...")
        
        if not check_ncalayer_running():
            self.show_error_message(f"Не удается запустить {robot_type} робота: NCALayer не найден.")
            return False
        
        try:
            success = start_robot_service(robot_instance, self.selected_path)
            if not success:
                self.show_error_message(f"Ошибка при выполнении робота {robot_type}")
                return False
            logger.info(f"Робот {robot_type} успешно завершил работу")
            return True
        except Exception as e:
            logger.error(f"Ошибка при выполнении робота {robot_type}: {str(e)}")
            self.show_error_message(f"Ошибка при выполнении робота {robot_type}: {str(e)}")
            return False

    def check_and_start_robot(self):
        """Проверка зависимостей и последовательный запуск роботов"""
        isna_enabled = os.getenv("ENABLE_ISNA", "false").lower() == "true"
        stat_enabled = os.getenv("ENABLE_STAT", "false").lower() == "true"
        knp_enabled = os.getenv("ENABLE_KNP", "false").lower() == "true"


        # Проверяем, включен ли хотя бы один режим
        if not knp_enabled and not stat_enabled and not isna_enabled:
            self.show_notification_message(
                "Необходимо выбрать хотя бы один режим работы!\n\n"
                "Текущее состояние:\n"
                "• ИСНА: Выключен\n"
                "• КНП: Выключен\n"
                "• СТАТ: Выключен\n\n"
                "Перейдите во вкладку настроек и включите нужные режимы."
            )
            return

        # Проверка выбранного пути
        if not hasattr(self, 'selected_path') or not self.selected_path:
            self.show_notification_message("Путь не выбран! Пожалуйста, укажите путь перед запуском.")
            return

        # Проверка интернет-соединения
        if not self.check_internet_connection():
            self.show_notification_message("Нет подключения к Интернету")
            return

        # Логируем с какими настройками запускается робот
        enabled_modes = []
        if isna_enabled:
            enabled_modes.append("ИСНА")
        if knp_enabled:
            enabled_modes.append("КНП")
        if stat_enabled:
            enabled_modes.append("СТАТ")
        
        logger.info(f"Запуск роботов в режимах: {', '.join(enabled_modes)}")



        # Последовательный запуск роботов
        isna_success = self.run_robot("ИСНА", self.robot_isna, start_robot_service_isna, isna_enabled)
        if isna_enabled and not isna_success:
            return
            
        knp_success = self.run_robot("КНП", self.robot_knp, start_robot_service_knp, knp_enabled)
        if knp_enabled and not knp_success:
            return
        
        stat_success = self.run_robot("СТАТ", self.robot_stat, start_robot_service_stat, stat_enabled)
        if stat_enabled and not stat_success:
            return


        self.show_notification_message("Все роботы успешно завершили работу!")

    def show_notification_message(self, message: str):
        """Показать уведомление."""
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
        notification_window = customtkinter.CTkToplevel(self)
        notification_window.title("Уведомление")
        notification_window.attributes('-topmost', True)
        
        notification_label = customtkinter.CTkLabel(notification_window, text=message)
        notification_label.pack(padx=20, pady=20)
        notification_button = customtkinter.CTkButton(notification_window, text="Закрыть", command=notification_window.destroy)
        notification_button.pack(pady=10)

    def show_error_message(self, message: str):
        """Показать сообщение об ошибке."""
        winsound.MessageBeep(winsound.MB_ICONHAND)
        error_window = customtkinter.CTkToplevel(self)
        error_window.title("Ошибка")
        error_window.attributes('-topmost', True)
        
        error_label = customtkinter.CTkLabel(error_window, text=message)
        error_label.pack(padx=20, pady=20)
        error_button = customtkinter.CTkButton(error_window, text="Закрыть", command=error_window.destroy)
        error_button.pack(pady=10)

    def select_path(self):
        """Открывает окно выбора директории и обновляет путь."""
        directory = filedialog.askdirectory(title="Выберите директорию")
        if directory:
            # Сохраняем путь в JSON и обновляем текст метки
            save_path_to_json(directory)
            self.selected_path = directory
            logger.info(f'Выбранный путь: {directory}')
            self.path_label.configure(text=directory)
        elif self.selected_path:
            # Если отменено, оставляем старый путь и выводим предупреждение
            logger.info(f'Путь не изменен: используется ранее сохраненный путь {self.selected_path}')
            self.path_label.configure(text=self.selected_path)
        else:
            # Если нет сохранённого пути, сообщаем об его отсутствии
            logger.info('Путь не выбран')
            self.path_label.configure(text="Путь не выбран")

    def select_frame_by_name(self, name):
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # Показываем выбранную страницу
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)