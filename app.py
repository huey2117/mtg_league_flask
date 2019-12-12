import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from service import CommanderService, DraftingService
from models import Schema

app = Flask(__name__)

"""
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


if __name__ == "__main__":
    print("main is actually running")
    app.debug = True
    print("DB tables should build next")
    Schema()
    app.run()
