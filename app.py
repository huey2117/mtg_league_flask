import os
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from service import CommanderService, DraftingService, UserService
from pgmodels import User, Roles, UserAdmin, RoleAdmin
from flask_security import Security, SQLAlchemySessionUserDatastore, login_required, utils, \
    current_user, login_user
from flask_security.forms import RegisterForm, Required, StringField, PasswordField, LoginForm
from database import db_session, init_db
from flask_mail import Mail, Message
from flask_admin import Admin


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', Required())


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['DEBUG'] = True
"""
On next restart of PC, env var for db_url and mail_password should be set.
Can clean this up then. Also clean up in database.py.
"""
if app.config['DEBUG']:
    postgres = {
        'user': 'dbtest',
        'password': 'devdbtest',
        'host': 'localhost',
        'port': '5432',
        'dbname': 'd8dndq07tlbq07'
    }
    db_url = f"postgresql://{postgres['user']}:{postgres['password']}@" \
        f"{postgres['host']}:{postgres['port']}/{postgres['dbname']}"
else:
    db_url = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SECURITY_PASSWORD_SALT'] = os.urandom(156)
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_TRACKABLE'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'noreply.fluffybunny@gmail.com'
app.config['MAIL_PASSWORD'] = 'nhjulbhjilfmdiyf'
# app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = ('Fluffy Bunny Admins', 'noreply.fluffybunny@gmail.com')
app.config['MAIL_MAX_EMAILS'] = 5
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'sandstone'
app.config['SECURITY_POST_LOGIN_VIEW'] = '/about'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/home'
app.config['SECURITY_POST_REGISTER_VIEW'] = '/about'

user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Roles)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)
mail = Mail(app)


@app.before_first_request
def before_first_request():
    init_db()
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='commissioner', description='League Commissioner')
    user_datastore.find_or_create_role(name='player', description='League Participant')
    user_datastore.find_or_create_role(name='scorekeeper', description='Designated Scorekeeper')

    # Testing Users and Roles
    # encrypted_password = utils.hash_password('testingflasksec')
    # if not user_datastore.get_user('michaelyeuh@gmail.com'):
    #     user_datastore.create_user(email='michaelyeuh@gmail.com', password=encrypted_password)
    # if not user_datastore.get_user('natelovin@gmail.com'):
    #     user_datastore.create_user(email='natelovin@gmail.com', password=encrypted_password)
    # if not user_datastore.get_user('scorekeeper@fakemail.com'):
    #     user_datastore.create_user(email='scorekeeper@fakemail.com', password=encrypted_password)
    # if not user_datastore.get_user('user@fbc.org'):
    #     user_datastore.create_user(email='user@fbc.org', password=encrypted_password)
    # db_session.commit()
    #
    # user_datastore.add_role_to_user('michaelyeuh@gmail.com', 'admin')
    # user_datastore.add_role_to_user('natelovin@gmail.com', 'commissioner')
    # user_datastore.add_role_to_user('scorekeeper@fakemail.com', 'scorekeeper')
    # user_datastore.add_role_to_user('user@fbc.org', 'player')
    # db_session.commit()


# Initialize Flask-Admin
admin = Admin(app)

# Add Flask-Admin views for Users and Roles
admin.add_view(UserAdmin(User, db_session))
admin.add_view(RoleAdmin(Roles, db_session))


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/home")
def home():
    # need to add this unless it will be handled by Vue/React
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember.data)
        return redirect(url_for('about'))
    return render_template('security/login_user.html', title='Sign In', form=form)


@app.route("/about", methods=["GET"])
@login_required
def about():
    return render_template('about.html')


@app.route("/draft", methods=["GET", "POST"])
@login_required
def draft():
    if request.method == 'POST':
        username = request.form['username']
        user_id = DraftingService().userid(username)
        if not user_id:
            error = 'Username does not exist. Please register or contact admin. '
            return render_template('draft.html', error=error)
        comm_check = DraftingService().usercomm(user_id)
        if comm_check:
            commander = comm_check
        else:
            commander = DraftingService().draft(user_id)

        return render_template('draft.html', commander=commander)

    else:
        return render_template('draft.html')


@app.route("/commanders", methods=["GET"])
@login_required
def commanders():
    return render_template('commanders.html')


@app.route("/commanders/create", methods=["GET","POST"])
@login_required
# @roles_required('admin', 'commissioner')
def create_commanders():
    if request.method == 'POST':
        comm_str = request.form.get("commlist").strip()
        comm_list = comm_str.split('\n')
        for comm in comm_list:
            comm = comm.strip()
            CommanderService().create(comm)

        return redirect(url_for('commanders'))
    else:
        return render_template('createcomm.html')


@app.route("/users", methods=["GET","POST"])
@login_required
def users():
    """
    This was the janky handling of security pre-flask-sec. Remove
    functionality once registration is live.
    """
    if request.method == 'POST':
        uid = request.form['user-id']
        sec = request.form['security'].lower()
        usn = request.form['username']
        if len(usn) > 30:
            error = 'Username must be less than 30 characters. '
            return render_template('users.html', error=error)

        if sec == 'juggernaut2117':
            params = (usn, int(uid))
            do_update = UserService().update_username(params)
            if do_update == 'invalid':
                error = 'User ID incorrect or invalid, please contact admin. '
                return render_template('users.html', error=error)
            elif do_update:
                flash(f'Username successfully updated to {usn}')
                return redirect(url_for('home'))
            else:
                error = "An error occurred while updating, please contact the admin. "
            return render_template('users.html', error=error)
        else:
            error = "Security check failed. "
            return render_template('users.html', error=error)
    else:
        return render_template('users.html')

@app.route("/register", methods=["GET","POST"])
@login_required
def register():
    lnames = ['huey','lovin','strzegowski']
    if request.method == 'POST':
        """
        Not currently in use for this iteration
        fname = request.form['fname']
        email = request.form['email']
        """
        lname = request.form['lname'].lower()
        usn = request.form['username']
        if len(usn) > 30:
            error = 'Username must be less than 30 characters. '
            return render_template('registration.html', error=error)
        sec = request.form['security'].lower()

        if sec == 'juggernaut2117' and lname in lnames:
            do_ins = UserService().create(usn)
            if do_ins == 'exists':
                flash('User already exists! ')
                return redirect(url_for('home'))
            elif do_ins:
                flash(f'User "{usn}" successfully created! ')
                return redirect(url_for('home'))
            else:
                error = 'User creation failed. Contact the admin. '
        else:
            error = 'Security check failed'

        return render_template('registration.html', error=error)
    else:
        return render_template('security/register_user.html')


@app.route("/resetpw", methods=["GET","POST"])
def reset_password():
    return render_template('security/reset_password.html')

if __name__ == "__main__":
    app.run()
