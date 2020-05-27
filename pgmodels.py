import os
import psycopg2
import random
from database import Base
from flask_security import UserMixin, RoleMixin, current_user, utils
from flask_security.forms import PasswordField
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, \
    ForeignKey, JSON, Date, PrimaryKeyConstraint
from flask_admin.contrib import sqla
from flask import redirect, url_for


test = True
db_url = os.environ['DATABASE_URL']
testdb_url = 'dbname=d8dndq07tlbq07 host=localhost port=5432 user=dbtest password=devdbtest'


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('admin.users.id'))
    role_id = Column('role_id', Integer(), ForeignKey('admin.roles.id'))


class Roles(Base, RoleMixin):
    __tablename__ = 'roles'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(Base, UserMixin):
    __tablename__ = 'users'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    email = Column(String(255), unique=True)
    first_name = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer())
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Roles', secondary='admin.roles_users',
                         backref=backref('admin.users', lazy='dynamic'))


class UserCommander(Base):
    __tablename__ = 'user_commander'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('admin.users.id'))
    commander_id = Column('commander_id', Integer(), ForeignKey('admin.commanders.id'))


class Commander(Base):
    __tablename__ = 'commanders'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), unique=True)
    color_identity = Column(String(9))
    link = Column(String(255))
    image_link = Column(String(255))
    scryfall_id = Column(String(64))


class DraftCommander(Base):
    __tablename__ = 'draft_commander'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    commander_id = Column('commander_id', Integer(), ForeignKey('admin.commanders.id'))


class RptStandings(Base):
    __tablename__ = 'rpt_standings'
    __table_args__ = ({"schema": "admin"})
    user_id = Column('user_id', Integer(), ForeignKey('admin.users.id'), primary_key=True)
    pts_total = Column(Integer())
    place_last_game = Column(Integer())
    pts_last_game = Column(Integer())


class RptCurrSeasonByGame(Base):
    __tablename__ = 'rpt_curr_season_by_game'
    __table_args__ = ({"schema": "admin"})
    user_id = Column(Integer(), primary_key=True)
    games = Column(JSON)
    first_bloods = Column(Integer())
    first_places = Column(Integer())
    second_places = Column(Integer())
    third_places = Column(Integer())
    fourth_places = Column(Integer())


class GamesScores(Base):
    __tablename__ = 'games_scores'
    __table_args__ = (PrimaryKeyConstraint('user_id', 'game_id'),
                      {"schema": "admin"})
    user_id = Column('user_id', Integer(), ForeignKey('admin.users.id'))
    game_id = Column('game_id', Integer(), ForeignKey('admin.games.id'))
    pts_total = Column(Integer())
    scores = Column(JSON())


class Games(Base):
    __tablename__ = 'games'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    season_id = Column('season_id', Integer(), ForeignKey('admin.seasons.id'))
    game_num = Column(Integer())
    budget = Column(Integer())
    flex = Column(Boolean)
    theme = Column(String(255))
    date = Column(Date())


class Seasons(Base):
    __tablename__ = 'seasons'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    name = Column(String(255))
    start_date = Column(Date())
    num_games = Column(Integer())
    is_current = Column(Boolean())
    winner_user_id = Column(Integer())


class UserAdmin(sqla.ModelView):

    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    # Don't include the standard password field when creating or editing a User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin') and current_user.is_authenticated

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login'))

    # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
    # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
    # we want to use a password field (with the input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.hash_password(model.password2)


# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):

    # Prevent administration of Roles unless the currently logged-in user has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')


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
        FROM draft_commanders dc
        LEFT JOIN admin.commanders c
            ON dc.commander_id = c.id
        LEFT JOIN admin.user_commander uc
            ON dc.commander_id = uc.commander_id
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


class Scoring:
    def __int__(self):
        if test:
            self.conn = psycopg2.connect(testdb_url)
        else:
            self.conn = psycopg2.connect(db_url, sslmode='require')
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        self.cur.close()

    def get_standings(self):
        query = """
        SELECT u.username,
                u.first_name,
                r.pts_total,
                r.place_last_game,
                r.pts_last_game
        FROM rpt_standings r
        LEFT JOIN users u
            ON r.user_id = u.user_id
        WHERE u.user_id IS NOT NULL
            AND u.active = True
        ;
        """

        self.cur.execute(query)
        standings = self.cur.fetchall()
        return standings


    # def update_standings(self, totals):
    #     """
    #     Adding the scores from a new game, only passing in the
    #     totals for each user for standings purposes. Totals should
    #     be a dict of form {'user_id': score, ...}
    #     """
    #     create_standings_backup = """
    #     CREATE TABLE tmp_standings_backup AS
    #     SELECT *
    #     FROM rpt_standings
    #     ;
    #     """
    #
    #     update_standings = """
    #
    #     """
    #
    #     self.cur.execute(create_standings_backup)
    #

#    def log_game(self, ):
