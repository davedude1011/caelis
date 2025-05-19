import sqlite3

connection = sqlite3.connect("data/userdata/userdata.db")
cursor = connection.cursor()

class UserData:
    def __init__(self, id: int, username: str, fullname: str, created_at: str):
        self.id = id
        self.username = username
        self.fullname = fullname
        self.created_at = created_at

def create_userdata(userid: int, username: str, fullname: str) -> None:
    cursor.execute("INSERT INTO users (id, username, fullname) VALUES (?, ?, ?)", (userid, username, fullname))
    connection.commit()

def get_userdata(userid: int) -> UserData | None:
    cursor.execute("SELECT * FROM users WHERE id = ?", (userid,))
    userdata = cursor.fetchone()

    if not userdata:
        return None
    return UserData(
        userdata[0],
        userdata[1],
        userdata[2],
        userdata[3],
    )