import sqlite3

connection = sqlite3.connect("data/imagedata/imagedata.db")
cursor = connection.cursor()

class Image:
    def __init__(self, id: int, collection_id: int, userid: int, width: int, height: int, filesize: int, fileid: str, created_at: str):
        self.id = id
        self.collection_id = collection_id
        self.userid = userid
        self.width = width
        self.height = height
        self.filesize = filesize
        self.fileid = fileid
        self.created_at = created_at
    
    def suicide(self):
        cursor.execute("DELETE FROM images WHERE id = ?", (self.id,))
        connection.commit()

class ImageCollection:
    def __init__(self, id: int, userid: int, title: str, active_multiselect: int, created_at: str):
        self.id = id
        self.userid = userid
        self.title = title
        self.active_multiselect = True if active_multiselect else False
        self.created_at = created_at
    
    def suicide(self):
        for image in self.get_images():
            image.suicide()

        cursor.execute("DELETE FROM collections WHERE id = ?", (self.id,))
        connection.commit()
    
    def get_images(self) -> list[Image]:
        cursor.execute("SELECT id, collection_id, userid, width, height, filesize, fileid, created_at FROM images WHERE collection_id = ?", (self.id,))
        return [
            Image(
                id, collection_id, userid, width, height, filesize, fileid, created_at,
            ) for (
                id, collection_id, userid, width, height, filesize, fileid, created_at,
            ) in cursor.fetchall()
        ]

    def create_image(self, width: int, height: int, filesize: int, fileid: str) -> None:
        cursor.execute("INSERT INTO images (collection_id, userid, width, height, filesize, fileid) VALUES (?, ?, ?, ?, ?, ?)", (self.id, self.userid, width, height, filesize, fileid,))
        connection.commit()
    
    def set_active_multiselect(self, value: bool) -> None:
        self.active_multiselect = value
        cursor.execute("UPDATE collections SET active_multiselect = ? WHERE id = ?", (1 if value else 0, self.id,))
        connection.commit()

class UserImageCollections:
    def __init__(self, userid: int):
        self.userid = userid

        if len(self.get_all_collections()) == 0:
            self.create_collection("default")
    
    def get_all_collections(self) -> list[ImageCollection]:
        cursor.execute("SELECT id, userid, title, active_multiselect, created_at FROM collections WHERE userid = ?", (self.userid,))
        return [
            ImageCollection(
                id, userid, title, active_multiselect, created_at,
            ) for (
                id, userid, title, active_multiselect, created_at,
            ) in cursor.fetchall()
        ]

    def get_collection(self, title: str) -> ImageCollection | None:
        cursor.execute("SELECT id, userid, title, active_multiselect, created_at FROM collections WHERE userid = ? AND title = ?", (self.userid, title,))
        data = cursor.fetchone()

        if not data:
            return None
        return ImageCollection(
            data[0],
            data[1],
            data[2],
            data[3],
            data[4],
        )

    def create_collection(self, title: str) -> None:
        cursor.execute("INSERT INTO collections (userid, title) VALUES (?, ?)", (self.userid, title,))
        connection.commit()