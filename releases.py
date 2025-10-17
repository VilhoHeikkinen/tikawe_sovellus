import db

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

def update_stars_avg(release_id):
    sql = """SELECT AVG(stars) FROM reviews
             WHERE release_id = ?"""
    result = db.query(sql, [release_id])
    avg = result[0][0]
    sql = "UPDATE releases SET stars_avg = ? WHERE id = ?"
    db.execute(sql, [avg, release_id])

def get_releases():
    sql = """SELECT re.id,
                    re.title,
                    re.artist,
                    re.type,
                    re.stars_avg,
                    COUNT(rv.id) AS review_count
                    FROM releases re
                    JOIN reviews rv ON re.id = rv.release_id
                    GROUP BY re.id
                    ORDER BY re.title"""
    return db.query(sql)

def get_release(release_id):
    sql = """SELECT re.title,
                    re.artist,
                    re.type,
                    re.stars_avg,
                    COUNT(rv.id) AS review_count
                    FROM releases re
                    JOIN reviews rv ON re.id = rv.release_id
                    WHERE re.id = ?
                    GROUP BY re.id
                    ORDER BY re.title"""
    result = db.query(sql, [release_id])
    return result[0] if result else None

def get_release_reviews(release_id):
    sql = """SELECT r.id,
                    r.artist,
                    r.album_name,
                    r.stars,
                    r.user_id,
                    u.username
             FROM reviews r, users u
             WHERE r.release_id = ? AND r.user_id = u.id
             ORDER BY r.id DESC"""
    return db.query(sql, [release_id])

def delete_release(release_id):
    sql = "DELETE FROM releases WHERE id = ?"
    db.execute(sql, [release_id])

def delete_releases_without_reviews(release_id):
    release_reviews = get_release_reviews(release_id)
    print("ASDASD", release_id)
    if not release_reviews:
        delete_release(release_id)
