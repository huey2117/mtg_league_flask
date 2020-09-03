from flask import Flask, request, render_template, redirect, \
    url_for, flash
from service import CommanderService, DraftingService, \
    ScoringService, InfoService, AdminService
from pgmodels import User, Roles, UserAdmin, RoleAdmin
from flask_security import Security, SQLAlchemySessionUserDatastore, \
    login_required, roles_accepted
from flask_security.forms import RegisterForm, Required, StringField
from database import db_session, init_db
from flask_mail import Mail
from flask_admin import Admin
import copy
import random


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', Required())


app = Flask(__name__)
app.config.from_pyfile('config.py')

"""
If DEBUG = True, set Test = True in pgmodel and database.
Really need to figure out a better way to do this.
"""
app.config['DEBUG'] = False

# Initialize SQLAlch Datastore
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Roles)

# Initialize Flask-Security
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)

# Initialize Flask-Mail
mail = Mail(app)

# Initialize Flask-Admin
admin = Admin(app)

# Add Flask-Admin views for Users and Roles
admin.add_view(UserAdmin(User, db_session))
admin.add_view(RoleAdmin(Roles, db_session))


@app.before_first_request
def before_first_request():
    init_db()


def update_standings():
    # This calls a full backup and rebuild of the rpt_standings table
    standings = ScoringService().rebuild_standings()
    if standings:
        return True


def restore_standings_from_backup():
    standings = ScoringService().restore_standings()
    if standings:
        return True


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about", methods=["GET"])
@login_required
def about():
    season_number, games_total, games_played = InfoService().get_curr_season_info()
    games_info = InfoService().get_games_info()
    games = [
        {"num": game[0],
         "theme": game[1],
         "budget": game[2]
         }
        for game in games_info
    ]
    standings = None
    get_standings = ScoringService().get_standings()
    if get_standings:
        standings = [
            {"username": row[0],
             "name": row[1],
             "pts_total": row[2],
             "place_last_game": row[3],
             "pts_last_game": row[4]
             }
            for row in get_standings
        ]

    curr_champ = None
    get_champ = InfoService().get_curr_champ()
    if get_champ:
        curr_champ = {
            "username": get_champ[0],
            "name": get_champ[1],
            "season_name": get_champ[2]
        }

    return render_template('about.html', snum=season_number, gp=games_played,
                           gt=games_total, games=games, standings=standings,
                           curr_champ=curr_champ)


@app.route("/draft", methods=["GET", "POST"])
@login_required
def draft():
    if request.method == 'POST':
        username = request.form['username']
        user_id = DraftingService().userid(username)
        if not user_id:
            flash(
                'Username does not exist. Please register or contact admin.',
                'danger'
            )
            return render_template('draft.html')

        comm_check = DraftingService().usercomm(user_id)
        commander = (
            comm_check if comm_check
            else DraftingService().draft(user_id)
        )

        return render_template('draft.html', commander=commander)

    else:
        return render_template('draft.html')


@app.route("/commanders", methods=["GET"])
@login_required
def commanders():
    comm_dicts = []
    commdb = CommanderService().comm_page_view()
    for row in commdb:
        d = {
            "name": row[0],
            "image": row[1],
            "link": row[2]
        }
        comm_dicts.append(d)
    return render_template('commanders.html', commanders=comm_dicts)


@app.route("/teams", methods=["GET"])
@login_required
def teams():
    teamdb = CommanderService().team_page()

    return render_template('teams.html', teams=teamdb)


@app.route("/commanders/create", methods=["GET", "POST"])
@login_required
@roles_accepted('admin', 'commissioner')
def create_commanders():
    # TODO: Fix method.
    # if request.method == 'POST':
    #     comm_str = request.form.get("commlist").strip()
    #     comm_list = comm_str.split('\n')
    #     for comm in comm_list:
    #         comm = comm.strip()
    #         CommanderService().create(comm)
    #
    #     return redirect(url_for('commanders'))
    # else:
    #     TODO: Finish template.
    #     return render_template('createcomm.html')
    return render_template('createcomm.html')


@app.route("/log_game", methods=["GET", "POST"])
@roles_accepted('admin', 'commissioner', 'scorekeeper')
def log_game():
    if request.method == 'POST':
        # Game Scores will be stored in the DB
        game_score = []

        # map username to user_id
        un_to_uid = {}
        pairs = ScoringService().get_uid_username_pairs()
        for row in pairs:
            un_to_uid[row[1]] = row[0]

        game_num_to_id = {}
        game_pairs = ScoringService().get_game_num_id()
        for row in game_pairs:
            game_num_to_id[row[1]] = row[0]

        # raw scoring template
        player_scores = {
            "user_id": 0,
            "game_id": 0,
            "username": '',
            "place": 0,
            "pts_total": 0,
            "first_blood": False,
            "commcast": False,
            "commfourplus": False,
            "save": 0,
            "commkill": False,
            "attlast": False,
            "killall": False,
            "popvote": False
        }

        # copy the scoring template
        p_one = copy.deepcopy(player_scores)
        p_two = copy.deepcopy(player_scores)
        p_three = copy.deepcopy(player_scores)
        p_four = copy.deepcopy(player_scores)

        # Fill player dictionaries and append to games list
        player_dict = {"p_one": "p1", "p_two": "p2", "p_three": "p3",
                       "p_four": "p4"}

        try:
            game_id = game_num_to_id[int(request.form['game_num'])]
        except KeyError:
            flash(f"Game number {request.form['game_num']} does not exist. "
                  f"Not logging scores for this match...", 'danger')
            return render_template('log_game.html')

        game_date = request.form['game_date']

        for k in player_dict:
            prefix = player_dict[k]
            if k == 'p_one':
                pdict = p_one
            elif k == 'p_two':
                pdict = p_two
            elif k == 'p_three':
                pdict = p_three
            elif k == 'p_four':
                pdict = p_four
            else:
                break

            pdict['username'] = request.form[f'{prefix}_username']
            pdict['user_id'] = un_to_uid[pdict['username']]
            pdict['game_id'] = game_id

            place_dict = {
                "1": 4,
                "2": 3,
                "3": 2,
                "4": 1
            }

            place = request.form[f'{prefix}_place']
            pdict['place'] = int(place)
            pdict['pts_total'] += place_dict[place]

            if request.form.get(f'{prefix}_firstblood', False):
                pdict['first_blood'] = True
                pdict['pts_total'] += 1

            if request.form.get(f'{prefix}_commcast', False):
                pdict['commcast'] = True

            if not pdict['commcast']:
                pdict['pts_total'] -= 1

            if request.form.get(f'{prefix}_commplus', False):
                pdict['commfourplus'] = True
                pdict['pts_total'] += 1

            saves = int(request.form[f'{prefix}_save'])
            pdict['save'] = saves
            pdict['pts_total'] += saves

            if request.form.get(f'{prefix}_commkill', False):
                pdict['commkill'] = True
                pdict['pts_total'] += 1

            if request.form.get(f'{prefix}_attlast', False):
                pdict['attlast'] = True
                pdict['pts_total'] -= 1

            if request.form.get(f'{prefix}_killall', False):
                pdict['killall'] = True
                pdict['pts_total'] -= 1

            if request.form.get(f'{prefix}_popvote', False):
                pdict['popvote'] = True
                pdict['pts_total'] += 1

            game_score.append(pdict)

        if len(game_score) == len(player_dict):
            num_scores = len(game_score)
            flash(f'Scores recorded for {num_scores} players. ', 'success')

        for score in game_score:
            uid = score['user_id']
            username = score['username']
            game_id = score['game_id']
            pts_total = score['pts_total']

            # log game + user record in db
            insert = ScoringService().add_scores(uid, game_id, pts_total,
                                                 score)
            if insert:
                flash(f'New score row successfully inserted for user: '
                      f'{username}.', 'success')
            else:
                flash(f'Something went wrong insert row for {username}, '
                      f'contact an admin.', 'danger')

        # log date of game in games table
        log_date = ScoringService().log_date(game_id, game_date)
        if log_date:
            print("Date updated for game. ")

        us = update_standings()
        if us:
            flash('Standings updated.', 'success')

        return render_template('log_game.html')
    else:
        return render_template('log_game.html')


@app.route('/rules', methods=['GET'])
def rules():
    # Page Includes:
    # Full Breakdown of Last Game
    # Current Season by Game
    # Scoring Ruleset Breakdown
    return render_template('rules.html')


@app.route('/season_admin', methods=['GET', 'POST'])
@roles_accepted('admin', 'commissioner')
def season_admin():
    next_season_name = None
    curr_season_name = None
    season_info = AdminService().get_season_info()
    try:
        curr_season_name = season_info[1]
        next_season_name = season_info[3]
    except:
        flash('Cannot retrieve season info', 'danger')

    return render_template('season_admin.html', next_season=next_season_name,
                           curr_season=curr_season_name)


@app.route('/create_season', methods=['POST'])
@roles_accepted('admin', 'commissioner')
def create_season():
    # redirects from create season form in season_admin
    params = {
        "season-name": request.form['season-name'],
        "num-games": int(request.form['num-games']),
        "start-date": request.form['start-date']
    }

    # Protecting myself from my own stupid data entry mistakes
    if 'season' not in params['season-name'].lower() \
            and len(params['season-name'] == 1):
        params['season-name'] = f"Season {params['season-name']}"

    create = AdminService().create_season(params)
    if create:
        fmsg = f"{params['season-name']} created. "
        state = 'success'
    else:
        fmsg = f"{params['season-name']} either already exists " \
               "or failed to create. "
        state = 'danger'
    flash(fmsg, state)
    return redirect(url_for('season_admin'))


@app.route('/challenges', methods=['GET', 'POST'])
@roles_accepted('admin', 'commissioner')
def challenges():
    if request.method == 'POST':
        num_challenges = random.randint(1, 3)
        challenges_sql = AdminService().roll_challenges(num_challenges)
        selected_challenges = [challenge[0] for challenge in challenges_sql]
        challenge_dict = {
            "num": num_challenges,
            "challenges": selected_challenges
        }

        season_info = AdminService().get_season_info()
        curr_season_name = season_info[1] or None
        next_season_name = season_info[3] or None

        return render_template('season_admin.html',
                               next_season=next_season_name,
                               curr_season=curr_season_name,
                               challenge_dict=challenge_dict
                               )

    else:
        return redirect(url_for('season_admin'))


@app.route('/add_games', methods=['POST'])
@roles_accepted('admin', 'commissioner')
def add_games_to_season():
    # redirects from add games form in season_admin
    season_number = request.form['add-season-games'].strip().lower()
    season_name = f'Season {season_number}'

    games = []
    gl = request.form['games-list'].strip().split('\r\n')
    for line in gl:
        line = line.split(',')
        flex = False
        if line[2].lower().strip() == 'yes':
            flex = True
        game = {
            "game_num": int(line[0].strip()),
            "budget": int(line[1].strip()),
            "flex": flex,
            "theme": line[3].strip()
        }
        games.append(game)

    num_games = len(games)
    params = {
        "season_name": season_name,
        "games": games
    }

    add = AdminService().add_games_to_season(params)
    if add == num_games:
        fmsg = f'{num_games} games added to {season_name}. '
        state = 'success'
    elif add != num_games:
        fmsg = f'Partial success. Only added {add} to {season_name}. '
        state = 'warning'
    else:
        fmsg = 'Failed to add games. '
        state = 'danger'

    flash(fmsg, state)
    return redirect(url_for('season_admin'))


@app.route('/start_season', methods=['POST'])
@roles_accepted('admin', 'commissioner')
def start_season():
    if request.method == 'POST':
        # end season placeholder
        new_season = AdminService().start_season()
        if new_season:
            fmsg = 'New Season Started'
            state = 'success'
            us = update_standings()
            if not us:
                flash('Standings update failed', 'danger')
        else:
            fmsg = 'Season cannot be started! '
            state = 'danger'

        flash(fmsg, state)
    return redirect(url_for('season_admin'))


@app.route('/log_decks', methods=['GET', 'POST'])
@roles_accepted('admin', 'commissioner', 'scorekeeper')
def log_decks():
    # TODO: Build decklist logger
    # Page Includes:
    # Logging Decks by User/Game
    # Anything else?
    return render_template('log_decks.html')


if __name__ == "__main__":
    app.run()
