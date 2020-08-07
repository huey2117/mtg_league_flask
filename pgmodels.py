import os
import psycopg2
import random
from database import Base
from flask_security import UserMixin, RoleMixin, current_user, utils
from flask_security.forms import PasswordField
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, \
    ForeignKey, JSON, Date, PrimaryKeyConstraint, UniqueConstraint
from flask_admin.contrib import sqla
from flask import redirect, url_for
import json

test = False
db_url = os.environ['DATABASE_URL']
try:
    testdb_url = os.environ['TESTDB_URL']
except:
    testdb_url = None


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
    commander_id = Column('commander_id', Integer(),
                          ForeignKey('admin.commanders.id'))


class Commander(Base):
    __tablename__ = 'commanders'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    name = Column(String(255), unique=True)
    color_identity = Column(String(16))
    cmc = Column(Integer())
    type_line = Column(String(255))
    is_partner = Column(Boolean)
    link = Column(String(255))
    image_link = Column(String(255))
    scryfall_id = Column(String(64))
    mtg_set = Column(String(4))
    set_name = Column(String(64))


class DraftCommander(Base):
    __tablename__ = 'draft_commander'
    __table_args__ = ({"schema": "admin"})
    id = Column(Integer(), primary_key=True)
    commander_id = Column('commander_id', Integer(),
                          ForeignKey('admin.commanders.id'))
    draft_rank = Column(Integer())


class RptStandings(Base):
    __tablename__ = 'rpt_standings'
    __table_args__ = ({"schema": "admin"})
    user_id = Column('user_id', Integer(), ForeignKey('admin.users.id'),
                     primary_key=True)
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
    __table_args__ = (UniqueConstraint('season_id', 'game_num'),
                      {"schema": "admin"})
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
    is_current = Column(Boolean(), default=False)
    winner_user_id = Column(Integer())


class UserAdmin(sqla.ModelView):
    # Don't display the password on the list of Users
    column_exclude_list = list = ('password',)

    # Don't include the standard password field when creating or editing a
    # User (but see below)
    form_excluded_columns = ('password',)

    # Automatically display human-readable names for the current and available
    # Roles when creating or editing a User
    column_auto_select_related = True

    # Prevent administration of Users unless the currently logged-in user has
    # the "admin" role
    def is_accessible(self):
        return (current_user.has_role('admin')
                and current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login'))

    # On the form for creating or editing a User, don't display a field
    # corresponding to the model's password field. There are two reasons
    # for this. First, we want to encrypt the password before storing in
    # the database. Second, we want to use a password field (with the
    # input masked) rather than a regular text field.
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've
        # already told Flask-Admin to exclude the password field from
        # this form.
        form_class = super(UserAdmin, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it
        # "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created
    # or edited User -- before the changes are committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank then encrypt the new password
        # prior to storing it in the database. If the password field is blank,
        # the existing password in the database will be retained.
        if len(model.password2):
            model.password = utils.hash_password(model.password2)


# Customized Role model for SQL-Admin
class RoleAdmin(sqla.ModelView):

    # Prevent administration of Roles unless the currently logged-in user
    # has the "admin" role
    def is_accessible(self):
        return current_user.has_role('admin')


class CommandersModel:
    tablename = "admin.commanders"

    def __init__(self):
        self.conn = (
            psycopg2.connect(testdb_url) if test
            else psycopg2.connect(db_url, sslmode='require')
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        self.cur.close()

    # TODO: None of this is in use as written, evaluate usage and cleanup
    # def get_by_id(self, _id):
    #     where_clause = f'AND id = {_id}'
    #     return self.select(where_clause)
    #
    # def create(self, params):
    #     query = f'INSERT INTO {self.tablename} ' \
    #             f'(name) ' \
    #             f'VALUES (%s)' \
    #         # f'"{params.get("color")}")'
    #     print("Next up, {}".format(params))
    #     params = (params,)
    #     result = self.cur.execute(query, params)
    #     return self.get_by_id(result.lastrowid)
    #
    # def delete(self, commander_id):
    #     query = f'DELETE FROM {self.tablename} ' \
    #             f'WHERE id = {commander_id}'
    #
    #     self.cur.execute(query)
    #     return
    #
    # def select(self, where_clause=''):
    #     query = f'SELECT name, color_id FROM {self.tablename} ' \
    #             + where_clause
    #
    #     self.cur.execute(query)
    #     result_set = self.cur.fetchall()
    #     result = [{column: row[i]
    #                for i, column in enumerate(result_set[0].keys())}
    #               for row in result_set]
    #     return result

    def comm_page_view(self):
        query = """
        SELECT c.name,
                c.image_link,
                c.link
        FROM admin.commanders c
        JOIN admin.draft_commander dc
            ON c.id = dc.commander_id
        WHERE dc.commander_id IS NOT NULL
        ORDER BY dc.draft_rank ASC
        ;
        """

        self.cur.execute(query)
        results = self.cur.fetchall()
        return results


class UsersModel:
    tablename = "admin.users"

    def __init__(self):
        self.conn = (
            psycopg2.connect(testdb_url) if test
            else psycopg2.connect(db_url, sslmode='require')
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        self.cur.close()


class UserDraftingModel:
    def __init__(self):
        self.conn = (
            psycopg2.connect(testdb_url) if test
            else psycopg2.connect(db_url, sslmode='require')
        )
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
        return result[0] or False

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
        return result[0] or False

    def draft_commander(self, uid):
        query = """
        SELECT c.id, c.name
        FROM admin.draft_commander dc
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
                        ;
                        """

            params = (uid, commander[0])
            self.cur.execute(update_query, params)
            return commander[1]
        else:
            return False


class ScoringModel:
    def __init__(self):
        self.conn = (
            psycopg2.connect(testdb_url) if test
            else psycopg2.connect(db_url, sslmode='require')
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        self.cur.close()

    def get_uid_username_pairs(self):
        query = """
        SELECT id, username
        FROM admin.users
        WHERE active = True
        ;
        """
        self.cur.execute(query)
        results = self.cur.fetchall()
        return results

    def add_scores(self, uid, game_id, pts_total, score):

        def check_scores(uid, game_id):
            query = f"SELECT * FROM admin.games_scores " \
                    f"WHERE user_id = {uid} " \
                    f"AND game_id = {game_id};"

            self.cur.execute(query)
            results = self.cur.fetchone
            return True if results else False

        score = json.dumps(score)

        query = f"INSERT INTO admin.games_scores " \
                f"(user_id, game_id, pts_total, scores) " \
                f"VALUES ({uid}, {game_id}, {pts_total}, '{score}') " \
                f"ON CONFLICT (user_id, game_id) " \
                f"DO UPDATE " \
                f"SET pts_total = EXCLUDED.pts_total, " \
                f"scores = EXCLUDED.scores; "

        self.cur.execute(query)
        check = check_scores(uid, game_id)

        return True if check else False

    def get_game_num_id(self):
        query = """
                SELECT g.id, g.game_num
                FROM admin.games g
                JOIN admin.seasons s
                    ON g.season_id = s.id
                WHERE s.is_current = True
                ;
                """
        self.cur.execute(query)
        results = self.cur.fetchall()
        return results

    def get_standings(self):
        query = """
        SELECT u.username,
                u.first_name,
                r.pts_total,
                r.place_last_game,
                r.pts_last_game
        FROM admin.rpt_standings r
        LEFT JOIN admin.users u
            ON r.user_id = u.id
        WHERE u.id IS NOT NULL
            AND u.active = True
        ORDER BY r.pts_total DESC,
            u.first_name ASC
        ;
        """

        self.cur.execute(query)
        standings = self.cur.fetchall()
        return standings

    def rebuild_standings(self):
        create_standings_backup = """
        CREATE TABLE IF NOT EXISTS admin.tmp_standings_backup 
        (LIKE admin.rpt_standings)
        ;
        """

        cleanup_backup = "DELETE FROM admin.tmp_standings_backup;"
        update_backup = """
        INSERT INTO admin.tmp_standings_backup
        SELECT * FROM admin.rpt_standings
        ;"""

        rebuild_standings = """
        WITH cte_curr (game_id) AS
        (SELECT g.id
        FROM admin.games g
        JOIN admin.seasons s
            ON g.season_id = s.id
        WHERE s.is_current = True),
        cte_mr (mr_game_id) AS
        (SELECT max(game_id) as mr_game_id
        FROM admin.games_scores)
        INSERT INTO admin.rpt_standings (user_id, pts_total, place_last_game, 
            pts_last_game)
        SELECT curr.user_id,
                curr.pts_total,
                mr.place_last_game,
                mr.pts_last_game
        FROM (SELECT gs.user_id,
                    sum(gs.pts_total) AS pts_total
            FROM admin.games_scores gs
            LEFT JOIN cte_curr c
                ON gs.game_id = c.game_id
            WHERE c.game_id IS NOT NULL
            GROUP BY gs.user_id
            ) as curr
        JOIN (SELECT gs.user_id,
                    gs.pts_total as pts_last_game,
                    (gs.scores->>'place')::INT as place_last_game
            FROM admin.games_scores gs
            LEFT JOIN cte_mr cm
                ON gs.game_id = cm.mr_game_id
            WHERE cm.mr_game_id IS NOT NULL
            ) as mr
            ON curr.user_id = mr.user_id
        WHERE mr.user_id IS NOT NULL
        ON CONFLICT (user_id) 
        DO UPDATE 
        SET pts_total = EXCLUDED.pts_total,
            place_last_game = EXCLUDED.place_last_game,
            pts_last_game = EXCLUDED.pts_last_game
        ;       
        """

        self.cur.execute(create_standings_backup)
        self.cur.execute(cleanup_backup)
        self.cur.execute(update_backup)
        self.cur.execute(rebuild_standings)

        return True

    def restore_standings(self):
        cleanup_sql = "DELETE FROM admin.rpt_standings;"

        restore_sql = """
        INSERT INTO admin.rpt_standings
        SELECT * 
        FROM admin.tmp_standings_backup
        ;
        """

        self.cur.execute(cleanup_sql)
        self.cur.execute(restore_sql)

    def log_date(self, game_id, game_date):
        update = """
        UPDATE admin.games
        SET date = %(gd)s
        WHERE id = %(gid)s
        ;
        """

        params = {"gd": game_date,
                  "gid": game_id
                  }

        self.cur.execute(update, params)
        return True


class InfoModel:
    def __init__(self):
        self.conn = (
            psycopg2.connect(testdb_url) if test
            else psycopg2.connect(db_url, sslmode='require')
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        self.cur.close()

    def get_curr_season_info(self):
        query = """
        SELECT s.name,
                count(DISTINCT g.id) as games_total,
                count(DISTINCT gs.game_id) as games_played
        FROM admin.seasons s
        JOIN admin.games g
            ON s.id = g.season_id
        LEFT JOIN admin.games_scores gs
            ON g.id = gs.game_id
        WHERE s.is_current = True
            AND g.id IS NOT NULL
        GROUP BY s.name
        ;"""

        self.cur.execute(query)
        results = self.cur.fetchone()
        return results

    def get_games_info(self):
        query = """
        SELECT g.game_num,
                g.theme,
                g.budget
        FROM admin.games g
        JOIN admin.seasons s
            on g.season_id = s.id
        WHERE s.is_current = True
        ORDER BY game_num ASC
        ;"""

        self.cur.execute(query)
        results = self.cur.fetchall()
        return results

    def get_curr_champ(self):
        query = """
        WITH cte_curr (prev_id) AS
        (SELECT id - 1 AS prev_id
        FROM ADMIN.seasons
        WHERE is_current = True)
        SELECT u.username,
                u.first_name,
                s.name
        FROM ADMIN.users u
        JOIN ADMIN.seasons s
            on u.id = s.winner_user_id
        JOIN cte_curr c 
            ON s.id = c.prev_id
        WHERE s.winner_user_id IS NOT NULL
        ;
        """
        self.cur.execute(query)
        results = self.cur.fetchone()
        return results or False


class AdminModel:
    def __init__(self):
        self.conn = (
            psycopg2.connect(testdb_url) if test
            else psycopg2.connect(db_url, sslmode='require')
        )
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()
        self.cur.close()

    def create_season(self, params):

        def check_insert(season_name):
            check_query = f"SELECT * FROM admin.seasons " \
                          f"WHERE name = '{season_name}' ;"

            self.cur.execute(check_query)
            results = self.cur.fetchone()

            return True if results else False

        query = """
        INSERT INTO admin.seasons (name, num_games, start_date)
        VALUES (%(season-name)s, %(num-games)s, %(start-date)s)
        ;
        """

        season_name = params['season-name']
        pre_check = check_insert(season_name)
        if not pre_check:
            self.cur.execute(query, params)
            check = check_insert(season_name)
            return True if check else False
        else:
            return False

    def add_games_to_season(self, params):

        def check_games(season_id):
            check_query = """
            SELECT count(*)
            FROM admin.games
            WHERE season_id = %(season_id)s
            ;
            """
            self.cur.execute(check_query, {"season_id": sid})
            result = self.cur.fetchone()
            return result[0] or False

        season_name = params['season_name']
        games = params['games']

        sid_query = """
        SELECT id
        FROM admin.seasons
        WHERE name = %(season_name)s
        ;
        """
        sid_params = {"season_name": season_name}
        self.cur.execute(sid_query, sid_params)
        res = self.cur.fetchone()

        if res:
            sid = res[0]
        else:
            return False

        for game in games:
            game['season_id'] = sid

        query = """
            INSERT INTO admin.games (season_id, game_num, budget, flex, theme)
            VALUES (%(season_id)s, %(game_num)s, %(budget)s, %(flex)s, 
            %(theme)s)
            ON CONFLICT (season_id, game_num)
            DO UPDATE
            SET budget = EXCLUDED.budget,
                flex = EXCLUDED.flex,
                theme = EXCLUDED.theme
            ;
            """
        self.cur.executemany(query, games)

        return check_games(sid)

    def get_season_info(self):
        query = """
        WITH cte_curr (curr_id, next_id) AS
        (SELECT s.id AS curr_id,
                s.id + 1 AS next_id
        FROM ADMIN.seasons s
        WHERE s.is_current = True)
        SELECT c.curr_id AS curr_id,
                s.name AS curr_name,
                c.next_id AS next_id,
                n.name AS next_name
        FROM cte_curr c
        JOIN ADMIN.seasons s 
            ON c.curr_id = s.id 
        LEFT JOIN ADMIN.seasons n 
            ON c.next_id = n.id
        ;
        """

        self.cur.execute(query)
        results = self.cur.fetchone()
        return results if results else False

    def start_season(self):
        season_info = self.get_season_info()
        if season_info[3]:
            new_active_id = season_info[2]
            old_active_id = season_info[0]

            # Check for games in the new season
            check_query = """
            SELECT count(*)
            FROM admin.games
            WHERE season_id = %(season_id)s
            ;
            """
            self.cur.execute(check_query, {"season_id": new_active_id})
            result = self.cur.fetchone()
            if not result:
                return False
            elif result[0] == 0:
                return False
            else:
                deactivate_query = """
                            WITH cte_winner (winner_user_id) AS
                            (SELECT user_id
                            FROM admin.rpt_standings
                            ORDER BY pts_total DESC
                            LIMIT 1)
                            UPDATE admin.seasons s
                            SET is_current = False,
                                winner_user_id = c.winner_user_id
                            FROM cte_winner c
                            WHERE s.is_current = True
                                AND s.id = %(sid)s
                            ;
                            """

                self.cur.execute(deactivate_query, {"sid": old_active_id})

                start_new_query = """
                UPDATE admin.seasons
                SET is_current = True
                WHERE id = %(sid)s
                ;
                """

                self.cur.execute(start_new_query, {"sid": new_active_id})
                return True
