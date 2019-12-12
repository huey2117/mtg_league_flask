import sqlite3


class Schema:
    def __init__(self):
        self.conn = sqlite3.connection("mtg_league.db")
        self.create_users_table()
        self.create_commanders_table()
        self.create_user_commander_table()

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    def create_user_commander_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS user_commander (
            user_id INTEGER NOT NULL,
            commander_id INTEGER NOT NULL,
            PRIMARY KEY(user_id, commander_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (commander_id) REFERENCES commanders (id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        ) WITHOUT ROWID
        ;
        """

        self.conn.execute(query)

    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            active TEXT NOT NULL
        )
        ;
        """

        self.conn.execute(query)

    def create_commanders_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS commanders (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            color_id TEXT NOT NULL
        )
        ;
        """

        self.conn.execute(query)


class CommandersModel:
    tablename = "commanders"

    def __init__(self):
        self.conn = sqlite3.connect('mtg_league.db')

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    def get_by_id(self, _id):
        where_clause = f'AND id = {_id}'
        return self.select(where_clause)

    def create(self, params):
        query = f'INSERT INTO {self.tablename} ' \
                f'(name, color_id) ' \
                f'VALUES ("{params.get("name")}",' \
                f'"{params.get("color")}")'

        result = self.conn.execute(query)
        return self.get_by_id(result.lastrowid)

    def delete(self, commander_id):
        query = f'DELETE FROM {self.tablename} ' \
                f'WHERE id = {commander_id}'

        self.conn.execute(query)
        return

    """
    # Excluding this function as update will not exist in this iteration
    def update(self, item_id, update_dict):
        set_query = " ".join([f'{column} = {value}'
                              for column, value in update_dict.items()])

        query = f"UPDATE {self.TABLENAME} " \
                f"SET {set_query} " \
                f"WHERE id = {item_id}"
        self.conn.execute(query)
        return self.get_by_id(item_id)
    """

    def select(self, where_clause=''):
        query = f'SELECT name, color_id FROM {self.tablename} ' \
                + where_clause

        result_set = self.conn.execute(query).fetchall()
        result = [{column: row[i]
                   for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result


class Users:
    tablename = "users"

    def __init__(self):
        self.conn = sqlite3.connect('mtg_league.db')

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def get_by_id(self, _id):
        where_clause = f'AND id = {_id}'
        return self.select(where_clause)

    def create_user(self, params):
        query = f'INSERT INTO {self.tablename} ' \
                f'(username, active) ' \
                f'VALUES ("{params.get("username")}",' \
                f'"{params.get("active")}")'

        result = self.conn.execute(query)
        return self.get_by_id(result.lastrowid)

    def update_user(self, user_id, update_dict):
        """
        column: value
        active: N
        """
        set_query = " ".join([f'{column} = {value}'
                              for column, value in update_dict.items()])

        query = f"UPDATE {self.tablename} " \
                f"SET {set_query} " \
                f"WHERE id = {user_id}"
        self.conn.execute(query)
        return self.get_by_id(user_id)
