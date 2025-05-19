from aiogram.types import User

from data.userdata.userdata import get_userdata as _get_userdata, create_userdata as _create_userdata
from data.imagedata.imagedata import UserImageCollections
from data.animedata.animedata import GlobalAnimeShows

class CaelisUser:
    def __init__(self, user: User) -> None:
        self.user = user

        if not _get_userdata(user.id):
            _create_userdata(user.id, user.username, user.full_name)
        
        self.image_collections = UserImageCollections(user.id)
    
    def get_userdata(self):
        return _get_userdata(self.user.id)