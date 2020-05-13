import os
import psycopg2
import random
from database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey

test = True

db_url = os.environ['DATABASE_URL']
testdb_url = 'dbname=d8dndq07tlbq07 host=localhost port=5432 user=dbtest password=devdbtest'


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('users.id'))
    role_id = Column('role_id', Integer(), ForeignKey('roles.id'))


class Roles(Base, RoleMixin):
    __tablename__ = 'roles'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer())
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Roles', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))


class Schema:
    def __init__(self):
        if test:
            self.conn = psycopg2.connect(testdb_url)
        else:
            self.conn = psycopg2.connect(db_url, sslmode='require')
        self.cur = self.conn.cursor()
        # self.create_users_table()
        self.create_commanders_table()
        self.create_user_commander_table()

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()
        self.cur.close()


    def create_user_commander_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS admin.user_commander (
            user_id INTEGER NOT NULL,
            commander_id INTEGER NOT NULL,
            PRIMARY KEY (user_id),
            FOREIGN KEY (user_id) REFERENCES admin.users (id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (commander_id) REFERENCES admin.commanders (id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
        ;
        """

        self.cur.execute(query)

    def create_users_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS admin.users (
            id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
            username VARCHAR(30) NOT NULL,
            active VARCHAR(1) DEFAULT 'A' CHECK (active IN ('A','I'))
        )
        ;
        """

        self.cur.execute(query)

    def create_commanders_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS admin.commanders (
            id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
            name VARCHAR(30) NOT NULL,
            color_id VARCHAR(5)
        )
        ;
        """

        self.cur.execute(query)


class CommandersModel:
    tablename = "admin.commanders"

    def __init__(self):
        if test:
            self.conn = psycopg2.connect(testdb_url)
        else:
            self.conn = psycopg2.connect(db_url, sslmode='require')
        self.cur = self.conn.cursor()

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()
        self.cur.close()

    def get_by_id(self, _id):
        where_clause = f'AND id = {_id}'
        return self.select(where_clause)

    def create(self, params):
        query = f'INSERT INTO {self.tablename} ' \
                f'(name) ' \
                f'VALUES (%s)' \
                # f'"{params.get("color")}")'
        print("Next up, {}".format(params))
        params = (params,)
        result = self.cur.execute(query, params)
        return self.get_by_id(result.lastrowid)

    def delete(self, commander_id):
        query = f'DELETE FROM {self.tablename} ' \
                f'WHERE id = {commander_id}'

        self.cur.execute(query)
        return

    """
    # Excluding this function as update will not exist in this iteration
    def update(self, item_id, update_dict):
        set_query = " ".join([f'{column} = {value}'
                              for column, value in update_dict.items()])

        query = f"UPDATE {self.TABLENAME} " \
                f"SET {set_query} " \
                f"WHERE id = {item_id}"
        self.cur.execute(query)
        return self.get_by_id(item_id)
    """

    def select(self, where_clause=''):
        query = f'SELECT name, color_id FROM {self.tablename} ' \
                + where_clause

        self.cur.execute(query)
        result_set = self.cur.fetchall()
        result = [{column: row[i]
                   for i, column in enumerate(result_set[0].keys())}
                  for row in result_set]
        return result


class UsersModel:
    tablename = "admin.users"

    def __init__(self):
        if test:
            self.conn = psycopg2.connect(testdb_url)
        else:
            self.conn = psycopg2.connect(db_url, sslmode='require')
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        self.cur.close()

    def get_by_id(self, id):
        where_clause = f'AND id = {id}'
        return self.select(where_clause)

    def select(self, where_clause=""):
        query = f'SELECT username FROM {self.tablename} ' \
                f'WHERE 1=1 ' + where_clause

        self.cur.execute(query)
        user = self.cur.fetchall()
        if user:
            return user[0]
        else:
            return user

    def create_user(self, username):
        where_clause = f"AND username = '{username}' "
        usn_duplicate_check = self.select(where_clause)
        if usn_duplicate_check:
            return 'exists'

        query = f'INSERT INTO {self.tablename} ' \
                f'(username) ' \
                f'VALUES (%s) '

        params = (username,)
        self.cur.execute(query, params)

        get_id = f'SELECT max(id) FROM {self.tablename} ' \
                f'WHERE username = %s'

        gid_params = (username,)
        self.cur.execute(get_id, gid_params)
        uid = self.cur.fetchone()
        return self.get_by_id(uid[0])

    def update_username(self, params):
        exists_check = self.get_by_id(params[1])
        if not exists_check:
            return 'invalid'

        query = f"UPDATE {self.tablename} " \
                f"SET username = %s " \
                f"WHERE id = %s"
        self.cur.execute(query, params)
        return self.get_by_id(params[1])


class UserDraftingModel:
    def __init__(self):
        if test:
            self.conn = psycopg2.connect(testdb_url)
        else:
            self.conn = psycopg2.connect(db_url, sslmode='require')
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        self.cur.close()

    def get_user_id(self, usn):
        query = f'SELECT id FROM admin.users ' \
                f'WHERE username = %s'

        params = (usn,)
        self.cur.execute(query, params)
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            return result

    def check_usercomm(self, uid):
        query = f'SELECT c.name ' \
                f'FROM admin.user_commander uc ' \
                f'LEFT JOIN admin.commanders c ' \
                f'ON uc.commander_id = c.id ' \
                f'WHERE uc.user_id = %s ' \
                f'AND uc.commander_id IS NOT NULL'

        params = (uid,)
        self.cur.execute(query, params)
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            return False

    def draft_commander(self, uid):
        query = """
        SELECT c.id, c.name
        FROM admin.commanders c
        LEFT JOIN admin.user_commander uc
            ON c.id = uc.commander_id
        WHERE uc.commander_id IS NULL
        """

        self.cur.execute(query)
        commanders = self.cur.fetchall()

        if commanders:
            commander = random.choice(commanders)
            update_query = """
                        INSERT INTO admin.user_commander
                        (user_id, commander_id)
                        VALUES (%s, %s)
                        ON CONFLICT (user_id)
                        DO UPDATE
                        SET commander_id = EXCLUDED.commander_id
                        """

            params = (uid, commander[0])
            self.cur.execute(update_query, params)
            return commander[1]
        else:
            return False
