CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    artist TEXT,
    album_name TEXT,
    genre TEXT,
    stars FLOAT,
    review TEXT,
    user_id INTEGER REFERENCES users
);