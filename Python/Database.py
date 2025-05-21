"""
Created for MySQL tried to make it easier to add other database types.
postgresql is not tested.
"""

class DatabaseConnector:
    def __init__(self, host="0.0.0.0", user="root", password="admin", database="table", database_type="mysql"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.database_type = database_type
        self.connection = None
        self.cursor = None

    def _connect_mysql(self):
        import mysql.connector
        mydb = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.connection = mydb
        return mydb

    def _connect_postgresql(self):
        import psycopg2
        mydb = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.connection = mydb
        return mydb

    def _connect_database(self):
        if self.database_type == "mysql":
            return self._connect_mysql()
        if self.database_type == "postgresql":
            return self._connect_postgresql()
        else:
            print("NO DATABASE TYPE SELECTED! Assuming mysql")
            return self._connect_mysql()

    def get_connection(self):
        self._connect_database()
        return self.connection

    def get_cursor(self):
        self.cursor = self._connect_database().cursor()
        return self.cursor

    def clear_connection(self):
        self.connection = None
        self.cursor = None

    def run_sql(self, sql: str) -> list:
        """
            Runs an sql statement and gives output of .fetchall.

            e.g.
                [
                    (1, 'tester'),
                    (2, 'test name')
                ]

            :param sql: input sql
            :return result: output 
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows

    def run_sql_dict_output(self, sql: str) -> list:
        """
        Runs an sql statement and gives output with coloumn names.

        e.g.
            [
                {'ClientId': 1, 'Name': 'tester'},
                {'ClientId': 2, 'Name': 'test name'}
            ]

        Can take longer to execute as creating the dict can take ages if a large query

        :param sql: input sql
        :return result: output as a dict with column names
        """
        with self._connect_database() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                # Fetch all rows from the executed query
                rows = cursor.fetchall()
                # Get column names from the cursor description
                column_names = [desc[0] for desc in cursor.description]
                # Create a list of dictionaries
                result = [dict(zip(column_names, row)) for row in rows]
                return result
