import threading

from src.python.services import data_control

__app_name__ = ""
__description__ = ""
__version__ = 0.1
__license__ = "MIT"
__author__ = ""
__author_email__ = ""


def main():
    """
    Starts the application
    """

    # Create the database object and runs the worker
    database = data_control.Database(r"C:\Users\caioq\Documents\Projeti-2022\data\database.db")

    database_worker_thread = threading.Thread(target=database.worker, daemon=True)
    database_worker_thread.start()


if __name__ == "__main__":
    main()
