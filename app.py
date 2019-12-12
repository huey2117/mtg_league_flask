import json

from flask import Flask, request, jsonify, render_template
from service import CommanderService
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
    return render_template('draft.html')


@app.route("/commanders", methods=["GET", "POST"])
def commanders():
    return render_template('commanders.html')
    """
    if request.method == 'POST':
        return jsonify(CommanderService().create(request.get_json))

    else:
        return jsonify(CommanderService().select())
    """


if __name__ == "__main__":
    # Schema()
    app.run(debug=True)
