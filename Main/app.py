import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

import requests, json

from helpers import apology, login_required, lookup, usd
from weathercode import weather

from flask_socketio import SocketIO, send

import requests
from flask_sqlalchemy import SQLAlchemy

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd


db = SQL("sqlite:///project.db")
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    """ home page if you had signed in """
    user_id = session["user_id"]

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Please input username!")

        elif not password:
            return apology("Please input password!")

        elif not confirmation:
            return apology("Please confirm password!")

        if password != confirmation:
            return apology("Password do not match!")

        hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            flash("Enter username and password!")
            return redirect("/")
        except:
            return apology("Username already exist!")
    else:
        return render_template("register.html")


"""  this is weather code section / sqlalchemy """

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        new_city = request.form.get('city')

        if new_city:
            db.execute("INSERT INTO city (name) VALUES (?)", new_city)

    cities = db.execute("SELECT name FROM city")

    # open weather app #------------------------------------#

    api_key = "8cd2d3f48fc469e28d3ba2eb8ba281d7"

    """ base_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1' """

    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    weather_data = []

    city = request.form.get('city')


    """ r = requests.get(url.format(city['name'])).json() """

    complete_url = base_url + "appid=" + api_key + "&q=" + str(city)

    response = requests.get(complete_url)

    x = response.json()

    city_name = str(city)
    temperature = x['main']['temp']
    description = x['weather'][0]['description']
    icon = x['weather'][0]['icon']

    print(city_name)
    print(temperature)
    print(description)
    print(icon)


    weather = {
        'city' : city_name,
        'temperature' : temperature,
        'description' : description,
        'icon' : icon,
    }

    """ weather = {
        'city' : cities,
        'temperature' : r['main']['temp'],
        'description' : r['weather'][0]['description'],
        'icon' : r['weather'][0]['icon'],
    } """

    weather_data.append(weather)
    print(weather)


    return render_template('weather.html', weather_data=weather_data)
