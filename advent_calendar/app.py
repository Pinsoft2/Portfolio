import os
import base64
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, jsonify, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__, static_url_path='/static')
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 7200
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
Session(app)

DATABASE_URL = os.environ.get('DATABASE_URL', 'project.db')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        account_password = request.form.get("account_password")

        if not username or not account_password:
            flash("Must provide username and password")
            return redirect("/register")

        db = get_db()
        try:
            # Insert new user
            db.execute(
                "INSERT INTO users (username, account_password_hash) VALUES (?, ?)",
                (username, generate_password_hash(account_password))
            )
            db.commit()

            # Get the new user's ID
            user = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()

            # Insert default passwords
            db.execute(
                "INSERT INTO user_settings (user_id, unlock_password, star_password) VALUES (?, ?, ?)",
                (user["id"], "cowboy", "Spy")
            )
            db.commit()

            flash("Registration successful!")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("Username already exists")
            return redirect("/register")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        account_password = request.form.get("account_password")

        # Check if it's an admin login
        if username == "admin" and account_password == "pp":
            session["user_id"] = "admin"
            session["is_admin"] = True
            return redirect("/admin")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and check_password_hash(user["account_password_hash"], account_password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session.permanent = True
            return redirect("/home")

        flash("Invalid username and/or password")
    return render_template("login.html")

@app.route("/check_password", methods=["POST"])
def check_password():
    password = request.form.get("password")
    if password == "pp" and session.get("username") == "admin":
        session["is_admin"] = True
        return jsonify({"success": True})

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False})

    db = get_db()
    settings = db.execute(
        "SELECT unlock_password FROM user_settings WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if settings and password == settings["unlock_password"]:
        session["initial_auth"] = True
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route("/home")
@login_required
def home():
    if not session.get("initial_auth"):
        # Pass an empty config when not authenticated
        return render_template("home.html", authenticated=False, calendar_config={})

    db = get_db()
    boxes = db.execute(
        "SELECT * FROM calendar_boxes WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    config = {}
    for box in boxes:
        config[str(box["box_number"])] = {
            "image": box["image_url"] if box["image_url"] else str(box["box_number"])
        }

    # Ensure all box numbers have an entry
    for i in range(1, 28):  # Changed to 28 to match heart layout
        if str(i) not in config:
            config[str(i)] = {"image": str(i)}

    return render_template("home.html", authenticated=True, calendar_config=config)

@app.route("/admin")
@login_required
def admin():
    db = get_db()
    settings = db.execute(
        "SELECT * FROM user_settings WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    boxes = db.execute(
        "SELECT * FROM calendar_boxes WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    config = {box["box_number"]: {
        "image": box["image_url"] if box["image_url"] else str(box["box_number"])
    } for box in boxes}

    return render_template("admin.html",
                         calendar_config=config,
                         unlock_password=settings["unlock_password"] if settings else "cowboy",
                         star_password=settings["star_password"] if settings else "Spy")

@app.route("/save_settings", methods=["POST"])
@login_required
def save_settings():
    unlock_password = request.form.get("unlock_password")
    star_password = request.form.get("star_password")

    db = get_db()
    db.execute("""
        UPDATE user_settings
        SET unlock_password = ?, star_password = ?
        WHERE user_id = ?
    """, (unlock_password, star_password, session["user_id"]))
    db.commit()

    return jsonify({"success": True})

@app.route("/save_box", methods=["POST"])
@login_required
def save_box():
    box_number = request.form.get("box_number")
    image_url = request.form.get("image_url")

    if not box_number:
        return jsonify({"error": "Missing box number"}), 400

    try:
        db = get_db()
        # Check if box exists
        existing = db.execute(
            "SELECT * FROM calendar_boxes WHERE user_id = ? AND box_number = ?",
            (session["user_id"], box_number)
        ).fetchone()

        if existing:
            # Print debug info
            print(f"Updating box {box_number} with image URL: {image_url}")
            db.execute("""
                UPDATE calendar_boxes
                SET image_url = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND box_number = ?
            """, (image_url, session["user_id"], box_number))
        else:
            # Print debug info
            print(f"Inserting new box {box_number} with image URL: {image_url}")
            db.execute("""
                INSERT INTO calendar_boxes (user_id, box_number, image_url)
                VALUES (?, ?, ?)
            """, (session["user_id"], box_number, image_url))

        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error saving box: {e}")  # For debugging
        return jsonify({"error": str(e)}), 500

@app.route("/check_unlock_password", methods=["POST"])
def check_unlock_password():
    if not session.get("user_id"):
        return jsonify({"success": False})

    password = request.form.get("password")
    user_id = session["user_id"]

    # First try to get user's custom unlock password
    db = get_db()
    settings = db.execute(
        "SELECT unlock_password FROM user_settings WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    # Check if password matches either the custom password or default 'cowboy'
    if (settings and password == settings["unlock_password"]) or password == "cowboy":
        session["initial_auth"] = True
        return jsonify({"success": True})

    return jsonify({"success": False})

@app.route("/check_star_password", methods=["POST"])
def check_star_password():
    if not session.get("user_id"):
        return jsonify({"success": False})

    password = request.form.get("password")
    user_id = session["user_id"]

    # Check for custom star password
    db = get_db()
    settings = db.execute(
        "SELECT star_password FROM user_settings WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    # Check if password matches either the custom password or default 'Spy'
    if (settings and password == settings["star_password"]) or password == "Spy":
        session["star_unlocked"] = True
        return jsonify({"success": True})

    return jsonify({"success": False})

@app.route("/is_star_unlocked")
def is_star_unlocked():
    return jsonify({"unlocked": session.get("star_unlocked", False)})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('project.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)