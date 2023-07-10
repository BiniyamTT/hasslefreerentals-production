import os
import datetime
import json
import sqlite3

from cs50 import SQL
from flask import Flask, flash, jsonify,redirect, render_template, request, session
from flask_session import Session
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure application
app = Flask(__name__)

# Initialize Flask-Breadcrumbs
Breadcrumbs(app=app)

#Initialize asyncio loop
#loop = asyncio.get_event_loop()

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///rentals.db",connect_args={'check_same_thread': False})

# Create users table
db.execute  ("""
                CREATE TABLE IF NOT EXISTS users
                (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phonenumber TEXT NOT NULL,
                    telegram_id INTEGER,
                    usertype TEXT NOT NULL
                )
            """)

# Create equipments table
db.execute  ("""
                CREATE TABLE IF NOT EXISTS equipments(
                    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    owner_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    sub_category TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    license_plate_no INTEGER NOT NULL,
                    fuel_type TEXT NOT NULL,
                    hp INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    hourly_rate TEXT NOT NULL,
                    advance TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    location TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (owner_id) REFERENCES users(user_id)
                )
            """)


# Configure global usertypes
USER_TYPES = ["Lessor", "Lessee"]

# Configure global equipment status
STATUS = ['Available', 'Unavailable']


# Configure global equipment categories
CAT =   {
    "Asphalt": ["Asphalt Layer", "Asphalt Scrapper"],
    "Compaction": ["Single Drum Smooth Wheeled Roller","Double Drum Smooth Wheeled Roller", "Padfoot Roller", "Pneumatic Roller"],
    "Concrete and Masonry": ["Concrete Pump Truck", "Concrete Mixer Truck",],
    "Earthwork":["Chain Excavator", "Mini-Excavator", "Bull-Dozer", "Grader", "Loader", "Back Hoe"],
    "Trucks and Trailers":["Flat Bed Trucks", "Dump Trucks", "Low-bed Trucks"]
    }

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html", CAT = CAT)


# Register Users to Webapp
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
    
        # Ensure username was submitted
        if not request.form.get("username"):
                return apology("must provide username", 403)
        
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username is not already taken
        if len(rows) == 1:
            return apology("username already taken", 403)
        
        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation") :
            return apology("must provide password", 403)
        
        # Ensure password matches with confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords dont match", 403)
        
        # Register username and password hash into db
        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))
        email = request.form.get("email")
        phonenumber = request.form.get("phonenumber")
        usertype = request.form.get("usertype")
        id = '123'
        db.execute("INSERT INTO users(username, hash, email, phonenumber, telegram_id, usertype) VALUES(?, ?, ?, ?, ?, ?)", username, hash, email, phonenumber, id, usertype)
        # Redirect to login page
        flash("You were successfully registered, log in to continue")
        return render_template("login.html")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", usertypes = USER_TYPES)


# Log Users in
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

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
        session["user_id"] = rows[0]["user_id"]
        session["usertype"] = rows[0]["usertype"]
        
        # Redirect user to home page
        flash("Successfully logged in")
        return redirect('/')
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Log users out
@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


# Equipments page will let users browse equipments on database
@app.route("/equipments")
@login_required
def equipments():
    return render_template("equipments.html", CAT = CAT)


@app.route("/screturn")
def screturn():
    cat = request.args.get("cat")
    if cat:
        subcat = CAT[cat]       
    else:
        subcat = []
    return jsonify(subcat)


@app.route("/eqregister", methods=["GET", "POST"])
@login_required
def eqregister():
    if request.method == "POST":
        print(session['user_id'])
        print("----------------------------------------------------------")
        db.execute ("""
            INSERT INTO equipments(owner_id, category, sub_category, brand, model, license_plate_no, fuel_type, hp, year, hourly_rate, advance, duration, location, status)
            VALUES(:owner_id, :category, :sub_category, :brand, :model, :license_plate_no, :fuel_type, :hp, :year, :hourly_rate, :advance, :duration, :location, :status)""",
                owner_id = session["user_id"],
                category= request.form.get("category"),
                sub_category = request.form.get("sub_category"),
                brand = request.form.get("brand"),
                model = request.form.get("model"),
                license_plate_no = request.form.get("license_plate_no"),
                fuel_type = request.form.get("fuel_type"),
                hp = request.form.get("hp"),
                year = request.form.get("year"),
                hourly_rate = request.form.get("hourly_rate"),
                advance = request.form.get("advance"),
                duration = request.form.get("duration"),
                location = request.form.get("location"),
                status = request.form.get("status")
        )
        return redirect ("/eqregister")
    else:
        return render_template("eqregister.html", CAT = CAT, STATUS = STATUS)
    
 
@app.route("/equipmentdetail", methods=["GET", "POST"])
@login_required
def equipmentdetail():
    if request.method == "GET":
        return render_template("equipmentdetail.html", CAT = CAT)
    else:
        cat = request.form.get('cat')
        sub_cat = request.form.get('sub_cat')
        rows = db.execute("SELECT * FROM equipments WHERE sub_category = ?", sub_cat)
        print(rows)
        return render_template("equipmentdetail.html", sub_category = sub_cat, CAT = CAT, equipments = rows)
    
if __name__ == "__main__":
    app.run(debug=False)