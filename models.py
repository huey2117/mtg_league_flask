import sqlite3
import random


class Schema:
    def __init__(self):
        self.conn = sqlite3.connect("mtg_league.db")
        self.create_users_table()
        self.create_commanders_table()
        self.create_user_commander_table()
        self.populate_users()

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
            color_id TEXT
        )
        ;
        """

        self.conn.execute(query)

    def populate_users(self):
        query = """
        INSERT OR REPLACE INTO users (username, active)
        VALUES ('michaelh','A'), ('nathanl','A'),
            ('matts','A'), ('jakel','A')
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
                f'(name) ' \
                f'VALUES (:name)' \
                # f'"{params.get("color")}")'
        print("Next up, {}".format(params))
        result = self.conn.execute(query, {"name": params})
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


class UserDraftingModel:
    def __init__(self):
        self.conn = sqlite3.connect('mtg_league.db')

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def get_user_id(self, usn):
        query = f'SELECT id FROM users ' \
                f'WHERE username = :usn'

        result = self.conn.execute(query, {"usn": usn}).fetchone()
        return result

    def check_usercomm(self, uid):
        query = f'SELECT c.name' \
                f'FROM user_commander uc' \
                f'LEFT JOIN commanders c' \
                f'ON uc.commander_id = c.id' \
                f'WHERE uc.user_id = :uid' \
                f'AND uc.commander_id IS NOT NULL'

        result = self.conn.execute(query, {"uid": uid}).fetchone()
        if result:
            return result
        else:
            return False

    def draft_commander(self, uid):
        query = """
        SELECT c.id, c.name
        FROM commanders c
        LEFT JOIN user_commander uc
            ON c.id = uc.commander_id
        WHERE uc.commander_id IS NULL
        """

        commanders = self.conn.execute(query).fetchall()
        if commanders:
            commander = random.choice(commanders)
            update_query = """
                        UPDATE user_commander
                        SET commander_id = :cid
                        WHERE user_id = :uid
                        """
            self.conn.execute(update_query, {"cid": commander[0], "uid": uid})
            return commander[1]
        else:
            return False
