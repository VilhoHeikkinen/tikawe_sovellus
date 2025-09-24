import db

def add_review(artist_name, album_name, genre, review, user_id):
    sql = """INSERT INTO reviews (artist, album_name, genre, review, user_id) 
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [artist_name, album_name, genre, review, user_id])

def get_reviews():
    sql = "SELECT id, artist, album_name FROM reviews ORDER BY id DESC"
    return db.query(sql)

def get_review(review_id):
    sql = """SELECT reviews.artist, 
                    reviews.album_name, 
                    reviews.genre, 
                    reviews.review,
                    users.username
             FROM reviews, users 
             WHERE reviews.user_id = users.id
             AND reviews.id = ?"""
    return db.query(sql, [review_id])[0]
