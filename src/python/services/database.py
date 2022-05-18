import sqlite3
from enum import Enum


class DatabaseTypes(Enum):
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    NULL = "NULL"
    BLOB = "BLOB"
    REAL = "REAL"


class DatabaseClass(object):
    def __init__(self, uid: int | None):
        self.primary_key = None
        self.id = uid

    def get_base_dict(self) -> dict:
        temp = self.__dict__
        temp.pop("primary_key", None)
        temp.pop("id", None)

        return temp

    def get_keys(self):
        return tuple(key.upper() for key in self.get_base_dict().keys())

    def get_values(self) -> tuple:
        return tuple(value for value in self.get_base_dict().values())

    def set_primary_key(self, key_name: str, key_type: DatabaseTypes, not_null: bool, auto_increment: bool):
        not_null_text = ""
        if not_null: not_null_text = "NOT NULL"

        auto_increment_text = ""
        if auto_increment: auto_increment_text = "AUTOINCREMENT"

        self.primary_key = {
            "attribute": f"{key_name.upper()} {key_type.value} {not_null_text} PRIMARY KEY {auto_increment_text}",
            "key_name": key_name.upper(),
            "key_type": key_type.value
        }

    def get_table_attributes(self) -> str:
        if self.primary_key is None:
            print("[DATA_CONTROL] Set a primary key before trying to get class attributes")
            return ""

        keys = self.get_keys()
        values = self.get_values()

        return_value = ""

        for i, key in enumerate(keys):
            if key == "PRIMARY_KEY":
                continue
            elif key == self.primary_key['key_name']:
                return_value += self.primary_key['attribute']
            elif type(values[i]) == str:
                return_value += f"{key} {DatabaseTypes.TEXT.value}"
            elif type(values[i]) == int:
                return_value += f"{key} {DatabaseTypes.INTEGER.value}"
            elif type(values[i]) is None:
                return_value += f"{key} {DatabaseTypes.NULL.value}"
            elif type(values[i]) == float:
                return_value += f"{key} {DatabaseTypes.REAL.value}"

            if len(keys) - 1 != i:
                return_value += ", "

        return return_value

    def get_class_name_upper(self) -> str:
        return self.__class__.__name__.upper()


class Database(object):
    """
    SQLite3 Vars: integer(int/bool(0/1)), text(string), null, real(float/double)
    """

    def __init__(self, connection_mode: str = None, database_path: str = None):
        self.database_path = database_path
        self.connection = self.connect_to_database(connection_mode)
        self.cursor = self.connection.cursor()

    def connect_to_database(self, mode: str = None) -> sqlite3.Connection:
        if mode is not None:
            if mode in ["test", "t", "Test"]:
                return sqlite3.connect(':memory:', check_same_thread=False)
        else:
            return sqlite3.connect(self.database_path, check_same_thread=False)

    @staticmethod
    def len_check(result: list, desired_len: int = 1) -> bool:
        if result is None:
            return False
        elif len(result) == desired_len:
            return True
        else:
            return False

    async def wipe_table(self, table_name: str):
        """
        Wipes all values from table

        EX: DELETE from test_table
        """
        with self.connection:
            self.cursor.execute(f"DELETE from {table_name}")

    async def create_table_from_class(self, ref_class: DatabaseClass):
        return await self.create_table(ref_class.get_class_name(), ref_class.get_table_attributes())

    async def create_table(self, table_name: str, table_attributes: str) -> str:
        """
        EX: CREATE TABLE test_table (column_name_1 variable_type, column_name_2 variable_type)

        EX: auto increment int = INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
        """
        with self.connection:
            try:
                self.cursor.execute(f"CREATE TABLE {table_name} ({table_attributes})")
                return f"[DATA_CONTROL] TABLE_NAME = {table_name} | TABLE_ATTRIBUTES = {table_attributes}"
            except sqlite3.OperationalError as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {table_name} | {table_attributes}")

    async def insert_value(self, table_name: str, database_class: DatabaseClass):
        """ EX: INSERT INTO test_table VALUES ('Maria', 'Joaquima', 300000) """
        with self.connection:
            try:
                self.cursor.execute(
                    f"INSERT INTO {table_name} {database_class.get_keys()} VALUES {database_class.get_values()}")
            except sqlite3.OperationalError as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {database_class.get_values()}")

    async def print_all_from_table(self, table_name: str) -> list:
        """
        EX: SELECT * from test_table
        """
        with self.connection:
            try:
                self.cursor.execute(f"SELECT * FROM {table_name}")
                return self.cursor.fetchall()
            except sqlite3.OperationalError as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {table_name}")

    async def print_from_param(self, table_name, search_params: tuple, search_params_2nd: tuple = None) -> list:
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
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE {param_str}")
                return self.cursor.fetchone()
            except sqlite3.OperationalError as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {param_str}")

    async def print_from_custom_value(self, table_name: str, select_param: str, search_params: tuple,
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
                self.cursor.execute(f"BACKUP DATABASE {database_name} TO DISK = '{path_to_backup}'{diff_str}")
            except sqlite3.OperationalError as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {database_name} | {path_to_backup} | {differential}")

    async def print_all_from_param(self, table_name: str, search_params: tuple,
                                   search_params_2nd: tuple = None) -> list:
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
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE {param_str}")
                return self.cursor.fetchall()
            except sqlite3.OperationalError as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {param_str}")

    async def remove_row(self, table_name, search_params: tuple, search_params_2nd: tuple = None):
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
                self.cursor.execute(f"DELETE from {table_name} WHERE {param_str}")
            except (Exception, sqlite3.ProgrammingError, sqlite3.OperationalError) as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {param_str}")

    async def update_value(self, table_name: str, value_to_change: str, new_value: str, search_params: tuple,
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
                self.cursor.execute(
                    f"""UPDATE {table_name} SET {value_to_change} = '{new_value}' WHERE {param_str}""")
            except (Exception, sqlite3.ProgrammingError, sqlite3.OperationalError) as e:
                print(f"[DATA_CONTROL] ERROR: {e} | VALUE: {value_to_change} - {new_value} - {param_str}")

    def close(self):
        self.connection.close()


database = Database(database_path="data/database.db")
