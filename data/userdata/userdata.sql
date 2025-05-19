CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    fullname TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);