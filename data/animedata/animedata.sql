CREATE TABLE shows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    title TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE episodes (
    id INTEGER,

    show_id INTEGER,
    
    title TEXT,
    episode INTEGER,
    season INTEGER,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);