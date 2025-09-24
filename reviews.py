import db

def add_review(artist_name, album_name, genre, review, user_id):
    sql = """INSERT INTO reviews (artist, album_name, genre, review, user_id) 
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [artist_name, album_name, genre, review, user_id])
    