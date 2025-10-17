CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    artist TEXT,
    album_name TEXT,
    stars FLOAT,
    year INTEGER,
    review TEXT,
    user_id INTEGER REFERENCES users,
    release_id INTEGER REFERENCES releases,
    image BLOB
);

CREATE TABLE review_classes (
    id INTEGER PRIMARY KEY,
    review_id INTEGER REFERENCES reviews,
    title TEXT,
    value TEXT
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE releases (
    id INTEGER PRIMARY KEY,
    title TEXT,
    artist TEXT,
    type TEXT,
    stars_avg FLOAT
);
