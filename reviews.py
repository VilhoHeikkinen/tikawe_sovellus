import db

def add_review(artist_name, album_name, stars, review, classes, user_id):
    sql = """INSERT INTO reviews (artist, album_name, stars, review, user_id)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [artist_name, album_name, stars, review, user_id])

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
                    reviews.review,
                    reviews.user_id,
                    users.username
             FROM reviews, users 
             WHERE reviews.user_id = users.id
             AND reviews.id = ?"""
    result = db.query(sql, [review_id])
    return result[0] if result else None

def get_classes(review_id):
    sql = "SELECT title, value FROM review_classes WHERE review_id = ?"
    result = db.query(sql, [review_id])
    return result if result else None

def edit_review(artist_name, album_name, stars, review, review_id, classes):
    sql = """UPDATE reviews SET artist = ?,
                                album_name = ?,
                                stars = ?,
                                review = ?
             WHERE id = ?"""
    db.execute(sql, [artist_name, album_name, stars, review, review_id])

    sql = """UPDATE review_classes SET title = ?,
                                       value = ?
             WHERE review_id = ?"""
    for title, value in classes:
        db.execute(sql, [title, value, review_id])

def delete_review(review_id):
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

def search(query):
    sql = """SELECT id, artist, album_name
             FROM reviews
             WHERE album_name LIKE ?
             ORDER BY id DESC"""
    return db.query(sql, ["%" + query + "%"])