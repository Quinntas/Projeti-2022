import queue
import sqlite3
import threading
import time
from enum import Enum


class Example_Client(object):
    """
    Use this class for reference when using this module

    Note that the class variable names are capitalized
    after version 1.5 it`s not necessary anymore
    """

    def __init__(self, username: str, login: str, password: str):
        self.Username = username
        self.Login = login
        self.Password = password


class Queue_Hint(Enum):
    NONE = 0
    INSERT_VALUE = 1
    UPDATE_VALUE = 2
    REMOVE_ROW = 3
    WIPE_TABLE = 6


def get_keys(class_dict: dict) -> tuple:
    return tuple(key.capitalize() for key in class_dict.keys())


def get_values(class_dict: dict) -> tuple:
    return tuple(value for value in class_dict.values())


class Database(object):
    """
    For reference

    SQLite3 Vars: integer(int/bool(0/1)), text(string), null, real(float/double)
    """

    def __init__(self, database_path: str, connection_mode: str = None) -> None:
        self.database_path = database_path
        self.connection = self.connect_to_database(connection_mode)
        self.cursor = self.connection.cursor()
        self.queue = queue.Queue()
        self.__exit__ = False
        self.lock = threading.Lock()

    def __repr__(self) -> str:
        return "Database Controller by Caio Quintas, all rights reserved"

    def __str__(self) -> str:
        return "Database Controller by Caio Quintas, all rights reserved"

    def connect_to_database(self, mode: str = None) -> sqlite3.Connection:
        if mode is not None:
            if mode in ["test", "t", "Test"]:
                return sqlite3.connect(':memory:', check_same_thread=False)
        else:
            return sqlite3.connect(self.database_path, check_same_thread=False)

    def wait_for_queue(self):
        while self.queue.qsize() >= 1:
            pass

    def add_to_queue(self, hint: Queue_Hint = Queue_Hint.NONE, table=None, queue_item: any = None,
                     queue_item_2: any = None) -> bool:
        """
        This function will return True if succeeded and False if not

        EX: add_to_queue(Queue_Hint.INSERT_VALUE, TABLES.LUNA_RESPONSES, a)

        EX UPDATE: add_to_queue(Queue_Hint.UPDATE_VALUE, TABLES.LUNA_RESPONSES, <Class>, ("response", "ee"))

        - queue_item_2 is NOT optional if you are updating a value
        - it uses a tuple for identifying the param you want to change and the value itself
        """
        if hint not in Queue_Hint:
            return False
        if hint == Queue_Hint.NONE:
            return False

        if hint == Queue_Hint.WIPE_TABLE:
            temp = [hint, table]
            self.queue.put(temp)
            return True

        if hint == Queue_Hint.UPDATE_VALUE:
            if queue_item_2 is None:
                return False
            if type(queue_item_2) != tuple:
                return False
            if len(queue_item_2) != 2:
                return False

        if hint == Queue_Hint.REMOVE_ROW or hint == Queue_Hint.UPDATE_VALUE:
            temp = [hint, table, queue_item]
        else:
            temp = [hint, table, queue_item.__dict__]

        if queue_item_2 is not None:
            temp.append(queue_item_2)

        self.queue.put(temp)
        return True

    def wipe_table(self, table_name: str):
        """
        Wipes all values from table

        EX: DELETE from test_table
        """
        with self.connection:
            self.cursor.execute(f"DELETE from {table_name}")

    def create_table(self, table_name: str, table_attributes: str):
        """
        EX: CREATE TABLE test_table (colum_name_1 variable_type, colum_name_2 variable_type)

        EX: auto increment int = INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
        """
        with self.connection:
            self.cursor.execute(f"CREATE TABLE {table_name} ({table_attributes})")

    def insert_value(self, table_name: str, value: dict):
        """ EX: INSERT INTO test_table VALUES ('Maria', 'Joaquina', 300000) """
        with self.connection:
            try:
                self.lock.acquire(True)
                self.cursor.execute(f"INSERT INTO {table_name} {get_keys(value)} VALUES {get_values(value)}")
            except sqlite3.OperationalError as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {value}")
                time.sleep(0.2)
                self.insert_value(table_name, value)
            finally:
                self.lock.release()

    def print_all_from_table(self, table_name: str) -> list:
        """
        EX: SELECT * from test_table
        """
        with self.connection:
            try:
                self.lock.acquire(True)
                self.cursor.execute(f"SELECT * FROM {table_name}")
                return self.cursor.fetchall()
            except sqlite3.OperationalError as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {table_name}")
                time.sleep(0.2)
                return self.print_all_from_table(table_name)
            finally:
                self.lock.release()

    def print_from_param(self, table_name, search_params: tuple, search_params_2nd: tuple = None) -> list:
        """
        EX: SELECT * from test_table WHERE pay = 10000 AND first_name = Caio

        EX: search_params = ('first_name', 'Caio')

        search_params_2nd are optional search params
        """
        param_str = f"{search_params[0]} = '{search_params[1]}'"
        if search_params_2nd is not None:
            param_str += f" AND {search_params_2nd[0]} = '{search_params_2nd[1]}'"
        with self.connection:
            try:
                self.lock.acquire(True)
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE {param_str}")
                return self.cursor.fetchone()
            finally:
                self.lock.release()

    def print_from_custom_value(self, table_name: str, select_param: str, search_params: tuple,
                                search_params_2nd: tuple = None) -> list:
        """
        EX: SELECT password from test_table WHERE user = 123

        EX: search_params = ('first_name', 'Caio')

        search_params_2nd are optional search params
        """
        param_str = f"{search_params[0]} = '{search_params[1]}'"
        if search_params_2nd is not None:
            param_str += f" AND {search_params_2nd[0]} = '{search_params_2nd[1]}'"
        with self.connection:
            self.cursor.execute(f"SELECT {select_param} FROM {table_name} WHERE {param_str}")
            return self.cursor.fetchall()

    def backup_database(self, database_name: str, path_to_backup: str, differential: bool = False):
        """
        Backs up database_name to path_to_backup
        """
        diff_str = ""
        if differential is True:
            diff_str = " WITH DIFFERENTIAL;"
        with self.connection:
            try:
                self.lock.acquire(True)
                self.cursor.execute(f"BACKUP DATABASE {database_name} TO DISK = '{path_to_backup}'{diff_str}")
            finally:
                self.lock.release()

    def print_all_from_param(self, table_name: str, search_params: tuple, search_params_2nd: tuple = None) -> list:
        """
        Returns all the values that matches with the params

        EX: SELECT * from test_table WHERE pay = 10000 AND first_name = Caio

        EX: search_params = ('first_name', 'Caio')

        search_params_2nd are optional search params
        """
        param_str = f"{search_params[0]} = '{search_params[1]}'"
        if search_params_2nd is not None:
            param_str += f" AND {search_params_2nd[0]} = '{search_params_2nd[1]}'"
        with self.connection:
            try:
                self.lock.acquire(True)
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE {param_str}")
                return self.cursor.fetchall()
            except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                time.sleep(0.2)
                self.print_all_from_param(table_name, search_params, search_params_2nd)
            finally:
                self.lock.release()

    def remove_row(self, table_name, search_params: tuple, search_params_2nd: tuple = None) -> list:
        """
        EX: DELETE from test_table WHERE pay = 10000 AND first_name = Caio

        EX: search_params = ('first_name', 'Caio')

        search_params_2nd are optional search params
        """
        param_str = f"{search_params[0]} = '{search_params[1]}'"
        if search_params_2nd is not None:
            param_str += f" AND {search_params_2nd[0]} = '{search_params_2nd[1]}'"
        with self.connection:
            try:
                self.lock.acquire(True)
                data = self.print_all_from_param(table_name, search_params, search_params_2nd)
                self.cursor.execute(f"DELETE from {table_name} WHERE {param_str}")
                return data
            finally:
                self.lock.release()

    def update_value(self, table_name: str, value_to_change: str, new_value: str, search_params: tuple,
                     search_params_2nd: tuple = None):
        """
        EX: UPDATE test_table SET pay = 10000 WHERE first_name = Caio

        EX: search_params = ('first_name', 'Caio')

        search_params_2nd are optional search params
        """
        param_str = f"{search_params[0]} = '{search_params[1]}'"
        if search_params_2nd is not None:
            param_str += f" AND {search_params_2nd[0]} = '{search_params_2nd[1]}'"

        with self.connection:
            try:
                self.lock.acquire(True)
                self.cursor.execute(
                    f"""UPDATE {table_name} SET {value_to_change} = '{new_value}' WHERE {param_str}""")
            except (Exception, sqlite3.ProgrammingError, sqlite3.OperationalError) as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {value_to_change} - {new_value} - {param_str}")
                time.sleep(0.2)
                self.update_value(table_name, value_to_change, new_value, search_params, search_params_2nd)
            finally:
                self.lock.release()

    def close(self):
        self.__exit__ = True
        self.connection.close()

    def worker(self, is_infinity: bool = True, stop_timer: int = 0):
        """
        :param is_infinity: Run forever
        :param stop_timer: Sleep after every check
        """
        while True:
            if self.queue.qsize() >= 1:
                q = self.queue.get()
                if q[0] == Queue_Hint.INSERT_VALUE:
                    self.insert_value(q[1].value, q[2])

                elif q[0] == Queue_Hint.UPDATE_VALUE:
                    self.update_value(q[1].value, q[3][0], q[3][1], (q[2][0], q[2][1]))

                elif q[0] == Queue_Hint.REMOVE_ROW:
                    self.remove_row(q[1].value, q[2])

                elif q[0] == Queue_Hint.WIPE_TABLE:
                    self.wipe_table(q[1].value)

            else:
                if is_infinity is False or self.__exit__ is True:
                    break
                time.sleep(stop_timer)
