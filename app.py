import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from service import CommanderService, DraftingService, UserService
# from models import Schema
from pgmodels import Schema

app = Flask(__name__)
app.secret_key = b'\xbdY]3\xba\xed\xdc\xe3\xe1\x1a\xaf\x84 o\x1dps\x8d\xb5|U\x8dW\xf8\x94bD\xce\xd9\x89\xc7\x1c'
"""
Need to take a second look at this portion
@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers," \
                                                       "Authorization, X-Requested-Width"
    response.headers['Access-Control-Allow-Methods'] = "POST, GET, PUT, DELETE, OPTIONS"
"""


@app.route("/")
def index():
    # need to add this unless it will be handled by Vue/React
    return render_template("home.html")


@app.route("/home")
def home():
    # need to add this unless it will be handled by Vue/React
    return render_template("home.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template('about.html')


@app.route("/draft", methods=["GET", "POST"])
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
def commanders():
    return render_template('commanders.html')


@app.route("/commanders/create", methods=["GET","POST"])
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
def users():
    if request.method == 'POST':
        uid = request.form['user-id']
        sec = request.form['security']
        usn = request.form['username']
        if len(usn) > 30:
            error = 'Username must be less than 30 characters. '
            return render_template('users.html', error=error)

        if sec == 'juggernaut2117':
            params = (usn, int(uid))
            do_update = UserService().update_username(params)
            if do_update:
                flash(f'Username successfully updated to {usn}')
                return redirect(url_for('home'))
            else:
                error = "Username does not exist or an error occurred while updating, please contact the admin. "
            return render_template('users.html', error=error)
        else:
            error = "Security check failed. "
            return render_template('users.html', error=error)
    else:
        return render_template('users.html')

@app.route("/register", methods=["GET","POST"])
def register():
    lnames = ['Huey','Lovin','Strzegowski']
    if request.method == 'POST':
        """
        Not currently in use for this iteration
        fname = request.form['fname']
        email = request.form['email']
        """
        lname = request.form['lname']
        usn = request.form['username']
        if len(usn) > 30:
            error = 'Username must be less than 30 characters. '
            return render_template('registration.html', error=error)
        sec = request.form['security']

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
        return render_template('registration.html')


if __name__ == "__main__":
    Schema()
    app.run()
