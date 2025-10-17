import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort, make_response
import db
import config
import reviews
import users
import releases
import maxlengths
import re

app = Flask(__name__)
app.secret_key = config.secret_key

def check_login():
    if "user_id" not in session:
        abort(403)

def check_id(id):
    session_id = session["user_id"] if "user_id" in session else None

    if id != session_id:
        abort(403)

def check_length(field, user_input):
    maxlength = maxlengths.map[field]
    if not maxlength:
        return
    if len(user_input) > maxlength:
        abort(403)

def get_image_from_file(file):
    if not (file.filename.endswith(".jpg") or file.filename.endswith(".jpeg")):
        return "VIRHE: väärä tiedostomuoto"
    image = file.read()
    if len(image) > 100 * 1024:
        return "VIRHE: liian suuri kuva"
    return image

@app.route("/")
def index():
    recent_reviews = reviews.get_reviews()
    classes = reviews.get_all_classes()
    return render_template("/index.html", reviews=recent_reviews, classes=classes)

@app.route("/new_review")
def new_review():
    check_login()
    classes = reviews.get_all_classes()
    return render_template("/new_review.html", classes=classes)

@app.route("/create_review", methods=["POST"])
def create_review():
    check_login()
    artist_name = request.form["artist"]
    album_name = request.form["album_name"]
    # Normalise artist_name and album_name
    normalised_artist = artist_name.strip().title()
    normalised_album = album_name.strip().title()

    file = request.files["image"]
    image = get_image_from_file(file)

    stars = request.form["stars"]
    # Check if stars is a number in between 0 and 5 with max one decimal place
    # and a comma or a dot is used
    if not re.search("^(?:[0-4](?:[.,]\d)?|5(?:\.0)?)$", stars):
        abort(403)
    publishing_year = request.form["year"]
    review = request.form["review"]

    for field, user_input in request.form.items():
        check_length(field, user_input)

    all_classes = reviews.get_all_classes()

    classes = []
    release_type = "NULL"
    addgenre = request.form.get("addgenre", "").strip()
    if addgenre:
        reviews.add_genre(addgenre)
        classes.append(("genre", addgenre))
    for item in request.form.getlist("classes"):
        if item:
            parts = item.split(":")
            if addgenre and parts[0] == "genre":
                continue
            if parts[0] not in all_classes:
                abort(403)
            if parts[1] not in all_classes[parts[0]]:
                abort(403)
            if parts[0] == "tyyppi":
                release_type = parts[1]
            classes.append((parts[0], parts[1]))

    releases.add_release(normalised_album, normalised_artist, release_type)
    release_id = releases.get_release_id(normalised_album, normalised_artist, release_type)
    reviews.add_review(normalised_artist,
                       normalised_album,
                       stars,
                       publishing_year,
                       review,
                       session["user_id"],
                       release_id,
                       image,
                       classes)
    releases.update_stars_avg(release_id)

    return redirect("/")

@app.route("/review/<int:review_id>")
def view_review(review_id):
    review = reviews.get_review(review_id)
    if not review:
        abort(404)
    classes = reviews.get_classes(review_id)
    return render_template("view_review.html", review=review, classes=classes)

@app.route("/edit/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    review = reviews.get_review(review_id)
    review_classes = reviews.get_classes(review_id)
    all_classes = reviews.get_all_classes()

    if not review:
        abort(404)

    check_id(review["user_id"])

    if request.method == "GET":
        return render_template("edit_review.html", review=review, review_classes=review_classes,
                               all_classes=all_classes)

    if request.method == "POST":
        artist_name = request.form["artist"]
        album_name = request.form["album_name"]
        # Normalise artist_name and album_name
        normalised_artist = artist_name.strip().title()
        normalised_album = album_name.strip().title()

        rm_img = request.form.get("rm_img")
        print(rm_img)
        if rm_img:
            image = ""
        else:
            file = request.files["image"]
            image = get_image_from_file(file)

        stars = request.form["stars"]
        # Check if stars is a number in between 0 and 5 with max one decimal place
        # and a comma or a dot is used
        if not re.search("^(?:[0-4](?:[.,]\d)?|5(?:\.0)?)$", stars):
            abort(403)
        publishing_year = request.form["year"]
        form_review = request.form["review"]

        for field, user_input in request.form.items():
            check_length(field, user_input)

        classes = []
        release_type = "NULL"
        addgenre = request.form.get("addgenre", "").strip()
        if addgenre:
            reviews.add_genre(addgenre)
            classes.append(("genre", addgenre))
        for item in request.form.getlist("classes"):
            if item:
                parts = item.split(":")
                if addgenre and parts[0] == "genre":
                    continue
                if parts[0] not in all_classes:
                    abort(403)
                if parts[1] not in all_classes[parts[0]]:
                    abort(403)
                if parts[0] == "tyyppi":
                    release_type = parts[1]
                classes.append((parts[0], parts[1]))

        # reviews.add_release only adds the release if it isn't in the table
        releases.add_release(normalised_album, normalised_artist, release_type)
        release_id = releases.get_release_id(normalised_album, normalised_artist, release_type)
        reviews.edit_review(normalised_artist,
                            normalised_album,
                            stars,
                            publishing_year,
                            form_review,
                            review_id,
                            release_id,
                            image,
                            classes)
        releases.update_stars_avg(release_id)

        # If release_id changed, and the old release doesn't have any
        # more reviews, delete the old release
        old_release_id = review["release_id"]
        if release_id != old_release_id:
            releases.delete_releases_without_reviews(old_release_id)
            # If the release still has reviews, update stars avg, otherwise this does nothing
            releases.update_stars_avg(old_release_id)

        return redirect(f"/review/{str(review_id)}")

@app.route("/remove/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    review = reviews.get_review(review_id)

    if not review:
        abort(404)

    check_id(review["user_id"])

    if request.method == "GET":
        return render_template("remove_review.html", review=review)

    if request.method == "POST":
        if "continue" in request.form:
            reviews.delete_review(review_id)
            release_id = review["release_id"]
            # Only delete release if it doesn't have any reviews after deleting one of them
            releases.delete_releases_without_reviews(release_id)
            releases.update_stars_avg(release_id)
            return redirect("/")
        if "cancel" in request.form:
            return redirect(f"/review/{str(review_id)}")

@app.route("/search")
def search():
    classes = reviews.get_all_classes()
    return render_template("/search.html", classes=classes)

@app.route("/search_reviews")
def search_reviews():
    query = request.args.get("query")
    classes = []
    for item in request.args.getlist("classes"):
        if item:
            parts = item.split(":")
            classes.append((parts[0], parts[1]))
    if query:
        searched_reviews = reviews.search(query, classes)
    else:
        query = ""
        searched_reviews = ""
    return render_template("/search_reviews.html", reviews=searched_reviews,
                           query=query, classes=classes)

@app.route("/user/<int:user_id>")
def view_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)

    user_reviews = users.get_reviews(user_id)
    return render_template("view_user.html", user=user, reviews=user_reviews)

@app.route("/view_releases")
def view_releases():
    all_releases = releases.get_releases()
    return render_template("/view_releases.html", releases=all_releases)

@app.route("/release/<int:release_id>")
def view_release(release_id):
    release = releases.get_release(release_id)
    release_reviews = releases.get_release_reviews(release_id)
    if not release:
        abort(404)
    return render_template("view_release.html", release=release, reviews=release_reviews)

@app.route("/image/<int:review_id>")
def show_image(review_id):
    image = reviews.get_image(review_id)
    if not image:
        abort(404)

    response = make_response(image)
    response.headers.set("Content-Type", "image/jpeg")
    return response

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

    try:
        users.create_user(username, password1)
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

        user_id = users.check_login(username, password)
        if user_id:
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
