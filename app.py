#!../venv/bin/python
import json

from flask import Flask, render_template, session, redirect, request, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash  # https://werkzeug.palletsprojects.com/en/2.2.x/utils/#module-werkzeug.security

from db import DB
from helpers import login_required, epochs_to_datetime, format_time

app = Flask(__name__)

# App configuration
app.secret_key = b'19deb93ac3a6f7d2aa61738b1adcf12d8eaa88c853f74820747a07db8e5aae77'  # Shouldn't be hardcoded
app.config["SESSION_PERMANENT"] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True  # Reloads templates and static files without restarting the server

# Adding jinja filtert to the jinja environment
# https://jinja.palletsprojects.com/en/3.0.x/api/#custom-filters
# jinja_env: https://flask.palletsprojects.com/en/2.2.x/api/
app.jinja_env.filters["epochs2dt"] = epochs_to_datetime
app.jinja_env.filters["format_time"] = format_time

db = DB()

@app.route("/")
@login_required
def index():
    """ Homepage """
    return render_template("pages/index.html")

@app.route("/ride")
@login_required
def ride():
    """ Start and track a ride """
    return render_template("pages/ride.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login existing user """
    session.clear()  # Just in case

    if request.method == "GET":
        return render_template("auth/login.html")

    db_user = db.get_user(request.form.get("username"))
    if not db_user:  # db_user is None
        flash("User doesn't exist", "danger")
        return render_template("auth/login.html")  # Redirection to same route doesn't show flash messages: https://github.com/pallets/flask/issues/1168

    if not check_password_hash(db_user[2], request.form.get("password")):
        flash("Wrong password", "danger")
        return render_template("auth/login.html")

    # On success, login
    session["user_id"] = db_user[0]
    session["username"] = db_user[1]
    session["rides"] = db_user[3]
    flash("Logged in!", "success")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Create a new user """
    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username")
    db_user = db.get_user(username)
    db_username = db_user[1] if db_user else None  # Solves None indexing error
    if username == db_username:
        flash("User already exists, try another username.", "danger")
        return redirect("/register")

    # On success, add user to database
    user_id = db.add_user(username, generate_password_hash(request.form.get("password")))

    # Login user
    session["user_id"] = user_id
    session["username"] = username
    session["rides"] = 0
    flash("Registered successfully!", "success")
    return redirect("/")

@app.route("/logout")
def logout():
    """ Logout and clear session dict """
    session.clear()
    flash("Logged out!", "info")
    return redirect("/login")

@app.route("/finish-ride", methods=["POST"])
@login_required
def finish_ride():
    """ AJAX: Ride finished """
    # Get the JSON object data from request data string
    ride = json.loads(request.data)

    db.add_ride(ride, session["user_id"])

    # Return empty json response
    return jsonify(success=True)

@app.route("/history")
@login_required
def history():
    """ See rides history """
    rides = db.get_history(session["user_id"])
    return render_template("pages/history.html", rides=rides)

@app.route("/view-ride")
@login_required
def view_ride():
    """ Get ride data by id and view ride info on a template """
    ride_data = db.get_ride(request.args.get("id"))
    return render_template("pages/view_ride.html", ride=ride_data)

if __name__ == "__main__":
    app.run(debug=False, ssl_context="adhoc", host="0.0.0.0")

