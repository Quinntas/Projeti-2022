import threading
from dotenv import load_dotenv
import os
from src.python.services import database_controller
from src.python.services.open_weather import get_climate_info

__app_name__ = ""
__description__ = ""
__version__ = 0.1
__license__ = "MIT"
__author__ = ""
__author_email__ = ""

load_dotenv()
OPEN_WEATHER_API_KEY = os.environ.get("OPEN_WEATHER_API_KEY")
IP_INFO_API_KEY = os.environ.get("IP_INFO_API_KEY")


def main():
    """
    Starts the application
    """

    # Create the database object and runs the worker
    database = database_controller.Database(r"C:\Users\caioq\Documents\Projeti-2022\data\database.db")

    database_worker_thread = threading.Thread(target=database.worker, daemon=True)
    database_worker_thread.start()


if __name__ == "__main__":
    main()
