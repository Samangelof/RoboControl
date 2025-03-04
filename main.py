from core.services.database.db_init import init_db
from gui.main_window import GuiRoboControl


if __name__ == "__main__":
    init_db()
    app = GuiRoboControl()
    app.mainloop()