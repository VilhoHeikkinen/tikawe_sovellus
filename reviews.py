import db

def add_review(artist_name, album_name, stars, publishing_year, review, user_id, release_id, classes):
    sql = """INSERT INTO reviews (artist, album_name, stars, year, review, user_id, release_id)
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [artist_name, album_name, stars, publishing_year, review, user_id, release_id])

    review_id = db.last_insert_id()

    sql = "INSERT INTO review_classes (review_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [review_id, title, value])

def get_reviews():
    sql = "SELECT id, artist, album_name, stars FROM reviews ORDER BY id DESC"
    return db.query(sql)

def get_review(review_id):
    sql = """SELECT reviews.id,
                    reviews.artist, 
                    reviews.album_name, 
                    reviews.stars,
                    reviews.year,
                    reviews.review,
                    reviews.user_id,
                    reviews.release_id,
                    users.username
             FROM reviews, users 
             WHERE reviews.user_id = users.id
             AND reviews.id = ?"""
    result = db.query(sql, [review_id])
    return result[0] if result else None

def get_release_reviews(release_id):
    sql = """SELECT id, artist, album_name, stars 
             FROM reviews 
             WHERE release_id = ?
             ORDER BY id DESC"""
    return db.query(sql, [release_id])

def edit_review(artist_name, album_name, stars, publishing_year, review, review_id, release_id, classes):
    sql = """UPDATE reviews SET artist = ?,
                                album_name = ?,
                                stars = ?,
                                year = ?,
                                review = ?,
                                release_id = ?
             WHERE id = ?"""
    db.execute(sql, [artist_name, album_name, stars, publishing_year, review, release_id, review_id])

    sql = """UPDATE review_classes SET value = ?
             WHERE title = ?
             AND review_id = ?"""
    for title, value in classes:
        db.execute(sql, [value, title, review_id])

def delete_review(review_id):
    sql = "DELETE FROM review_classes WHERE review_id = ?"
    db.execute(sql, [review_id])
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

def search(query):
    sql = """SELECT id, artist, album_name
             FROM reviews
             WHERE album_name LIKE ?
             ORDER BY id DESC"""
    return db.query(sql, ["%" + query + "%"])

def get_classes(review_id):
    sql = "SELECT title, value FROM review_classes WHERE review_id = ?"
    result = db.query(sql, [review_id])
    return {row["title"]: row["value"] for row in result}

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY value"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)
    return classes

def add_genre(genre):
    sql = "INSERT INTO classes (title, value) VALUES (?, ?);"
    db.execute(sql, ["genre", genre])

def add_release(title, artist_name, release_type):
    sql = "SELECT title, artist, type FROM releases WHERE title = ? AND artist = ? AND type = ?"
    result = db.query(sql, [title, artist_name, release_type])

    if result:
        return

    sql = "INSERT INTO releases (title, artist, type, stars_avg) VALUES (?, ?, ?, NULL)"
    db.execute(sql, [title, artist_name, release_type])

def get_release_id(title, artist_name, release_type):
    sql = "SELECT id FROM releases WHERE title = ? AND artist = ? AND type = ?"
    result = db.query(sql, [title, artist_name, release_type])
    return result[0][0]

def add_stars_avg(title, artist_name, release_type):
    sql = """SELECT AVG(r.stars) FROM reviews r, review_classes c
             WHERE r.album_name = ? AND r.artist = ?
             AND c.value = ?
             AND c.review_id = r.id"""
    result = db.query(sql, [title, artist_name, release_type])
    avg = result[0][0]
    sql = "UPDATE releases SET stars_avg = ? WHERE title = ? AND artist = ? AND type = ?"
    db.execute(sql, [avg, title, artist_name, release_type])

def get_releases():
    sql = "SELECT id, title, artist, type, stars_avg FROM releases ORDER BY title"
    return db.query(sql)

def get_release(release_id):
    sql = """SELECT title, artist, type, stars_avg FROM releases
             WHERE id = ?"""
    result = db.query(sql, [release_id])
    return result[0] if result else None

def delete_release(release_id):
    sql = "DELETE FROM releases WHERE id = ?"
    db.execute(sql, [release_id])
