import sqlite3
from rapidfuzz import process, fuzz

connection = sqlite3.connect("data/animedata/animedata.db")
cursor = connection.cursor()

class AnimeEpisode:
    def __init__(self, id: int, show_id: int, title: str, episode: int, season: int):
        self.id = id
        self.show_id = show_id
        self.title = title
        self.episode = episode
        self.season = season

class AnimeShow:
    def __init__(self, id: int, title: str, episodes: list[AnimeEpisode] = []):
        self.id = id
        self.title = title
        self.episodes = episodes

        if len(episodes) == 0:
            self.populate_episodes()
    
    def populate_episodes(self):
        cursor.execute("SELECT id, show_id, title, episode, season FROM episodes WHERE show_id = ?", (self.id,))
        self.episodes = [
            AnimeEpisode(
                id, show_id, title, episode, season
            ) for (
                id, show_id, title, episode, season
            ) in cursor.fetchall()
        ]
    
    def list_episodes(self) -> str:
        return "\n".join([f"<i>{_.id}</i>. <code>ep{_.episode} - {_.title}</code>" for _ in self.episodes]) or "wada hell?? nothing was found for some reason :I"

class GlobalAnimeShows:
    def __init__(self, shows: list[AnimeShow] = []):
        self.shows = shows

        if len(shows) == 0:
            self.populate_shows()

    def populate_shows(self):
        cursor.execute("SELECT id, title FROM shows")
        self.shows = [
            AnimeShow(
                id, title
            ) for (
                id, title
            ) in cursor.fetchall()
        ]
    
    def list_shows(self, search: str | None):
        if not self.shows:
            return "Nothing found :-("

        if not search:
            return "\n".join([f"<i>{s.id}</i>. <code>{s.title}</code>" for s in self.shows])

        # Case-insensitive mapping
        title_map = {s.title.lower(): s for s in self.shows}

        results = process.extract(
            query=search.lower(),
            choices=list(title_map.keys()),
            scorer=fuzz.partial_ratio,
            score_cutoff=60
        )

        if not results:
            return "Nothing found :-("

        return "\n".join(
            [f"<i>{title_map[title].id}</i>. <code>{title_map[title].title}</code>" for title, _, _ in results]
        )

    def get_show(self, show_id: int) -> AnimeShow | None:
        for show in self.shows:
            if show.id == show_id:
                return show
        return None

GLOBAL_ANIME_SHOWS = GlobalAnimeShows()