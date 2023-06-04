import psycopg2


class MyDbPostgreSql:
    def __init__(self, host="127.0.0.1", user="postgres", password="", db_name=""):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

        self.connection = None
        self.cursor = None

    def open(self) -> None:

        try:
            self.connection = psycopg2.connect(host=self.host, user=self.user,
                                               password=self.password, database=self.db_name)
            self.cursor = self.connection.cursor()

        except psycopg2.DatabaseError as e:
            if self.connection:
                self.connection.rollback()

            print("Can't connect to db:")
            print(f'Error {e}')

    def close(self) -> None:
        self.connection.close()

    def create_table(self, table_name: str, table_structure: str) -> None:

        query = "CREATE TABLE " + table_name + table_structure
        self.open()
        self.cursor.execute("DROP TABLE IF EXISTS {0}".format(table_name))
        self.cursor.execute(query)
        self.connection.commit()
        self.close()

    def insert(self, table, *args, **kwargs) -> None:

        values = None
        query = f'INSERT INTO {table} '
        if kwargs:
            keys = kwargs.keys()
            values = tuple(kwargs.values())
            query += "(" + ",".join(["%s"] * len(keys)) % tuple(keys) + \
                     ") VALUES (" + ",".join(["%s"] * len(values)) + ")"
        elif args:
            values = args
            query += " VALUES(" + ",".join(["%s"] * len(values)) + ")"

        self.open()
        self.cursor.execute(query, values)
        self.connection.commit()
        self.close()

        print("Successfully saved to DB")
