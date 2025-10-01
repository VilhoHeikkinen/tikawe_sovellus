import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import reviews

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    recent_reviews = reviews.get_reviews()
    return render_template("/index.html", reviews = recent_reviews)

@app.route("/new_review")
def new_review():
    return render_template("/new_review.html")

@app.route("/create_review", methods=["POST"])
def create_review():
    artist_name = request.form["artist"]
    album_name = request.form["album_name"]
    genre = request.form["genre"]
    stars = request.form["stars"]
    review = request.form["review"]

    reviews.add_review(artist_name, album_name, genre, stars, review, session["user_id"])

    return redirect("/")

@app.route("/review/<int:review_id>")
def view_review(review_id):
    review = reviews.get_review(review_id)
    if not review:
        abort(404)
    return render_template("view_review.html", review=review)

@app.route("/edit/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    review = reviews.get_review(review_id)

    if not review:
        abort(404)

    current_id = review["user_id"]
    try:
        session_id = session["user_id"]
    except KeyError:
        session_id = None

    if current_id != session_id:
        abort(403)

    if request.method == "GET":
        return render_template("edit_review.html", review=review)

    if request.method == "POST":
        artist_name = request.form["artist"]
        album_name = request.form["album_name"]
        genre = request.form["genre"]
        stars = request.form["stars"]
        review = request.form["review"]
        reviews.edit_review(artist_name, album_name, genre, stars, review, review_id)
        return redirect(f"/review/{str(review_id)}")

@app.route("/remove/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    review = reviews.get_review(review_id)

    if not review:
        abort(404)

    current_id = review["user_id"]
    try:
        session_id = session["user_id"]
    except KeyError:
        session_id = None

    if current_id != session_id:
        abort(403)

    if request.method == "GET":
        return render_template("remove_review.html", review=review)

    if request.method == "POST":
        if "continue" in request.form:
            reviews.delete_review(review_id)
            return redirect("/")
        if "cancel" in request.form:
            return redirect(f"/review/{str(review_id)}")
  
@app.route("/search_reviews")
def search_reviews():
    query = request.args.get("query")
    if query:
        searched_reviews = reviews.search(query)
    else:
        query = ""
        searched_reviews = ""
    return render_template("/search_reviews.html", reviews=searched_reviews, query=query)

@app.route("/register")
def register():
    return render_template("/register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("/login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")
