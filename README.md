# RoboControl

Модульная система для автоматизации бизнес-процессов с использованием роботов. Программное обеспечение позволяет контролировать действия роботов, настраивать их поведение и собирать аналитику.

- Архитектура — слоистая, сервис-ориентированная
- GUI — на CustomTkinter
- Взаимодействие с веб — через Selenium
- Отчеты — в формате Excel
 Отстук — Telegram

## Возможности

- Расширяемая модульная архитектура
- Сервисная ориентация: четкое разделение логики, GUI и настроек
- Графический интерфейс на базе CustomTkinter
- Автоматизация браузерных сценариев с помощью Selenium
- Генерация и сохранение отчетов в `report.xlsx`
- Поддержка кастомных настроек через `config.json`

## Требования

- Python 3.9+
- Библиотеки из `requirements.txt`

## Установка

1. Клонировать репозиторий
   ```bash
   git clone https://github.com/Samangelof/RoboControl.git
   cd RoboControl
   ```
2. Создать и активировать виртуальное окружение
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/Mac
   venv\Scripts\activate       # Windows
   ```
3. Установить зависимости
   ```bash
   pip install -r requirements.txt
   ```

## Запуск

- Выполнить
  ```bash
  python main.py
  ```

## Контакты
- GitHub: https://t.me/Samangelof
