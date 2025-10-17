import db

def add_review(artist_name, album_name, stars, publishing_year, review, user_id, release_id, image, classes):
    sql = """INSERT INTO reviews
             (artist, album_name, stars, year, review, user_id, release_id, image)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [artist_name, album_name, stars,
                     publishing_year, review, user_id, release_id, image])

    review_id = db.last_insert_id()

    sql = "INSERT INTO review_classes (review_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [review_id, title, value])

def get_reviews():
    sql = """SELECT r.id,
                    r.artist,
                    r.album_name,
                    r.stars,
                    r.user_id,
                    u.username
             FROM reviews r, users u
             WHERE r.user_id = u.id
             ORDER BY r.id DESC"""
    return db.query(sql)

def get_review(review_id):
    sql = """SELECT reviews.id,
                    reviews.artist, 
                    reviews.album_name, 
                    reviews.image IS NOT NULL has_image,
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

def edit_review(artist_name, album_name, stars, publishing_year, review, review_id, release_id, image, classes):
    sql = """UPDATE reviews SET artist = ?,
                                album_name = ?,
                                stars = ?,
                                year = ?,
                                review = ?,
                                release_id = ?,
                                image = ?
             WHERE id = ?"""
    db.execute(sql, [artist_name, album_name, stars, publishing_year,
                     review, release_id, image, review_id])

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

def search(query, classes):
    sql = """SELECT r.id,
                    r.artist,
                    r.album_name,
                    r.stars,
                    r.user_id,
                    u.username
             FROM reviews r, users u
             WHERE r.user_id = u.id
             AND (album_name LIKE ? OR artist LIKE ?)"""
    params = ["%" + query + "%", "%" + query + "%"]

    for title, value in classes:
        sql += """ AND EXISTS
                   (SELECT title, value
                   FROM review_classes c
                   WHERE c.review_id = r.id
                   AND c.title = ?
                   AND c.value = ?)"""
        params += [title, value]

    sql += " ORDER BY r.id DESC"

    return db.query(sql, params)

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

def get_image(review_id):
    sql = "SELECT image FROM reviews WHERE id = ?"
    result = db.query(sql, [review_id])
    return result[0][0] if result else None
