CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER,
    
    title TEXT,
    active_multiselect BOOLEAN DEFAULT 0,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER,
    userid INTEGER,

    width INTEGER,
    height INTEGER,
    filesize INTEGER,
    fileid TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);