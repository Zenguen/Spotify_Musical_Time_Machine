from bs4 import BeautifulSoup
import requests as req
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

uri = os.getenv('SPOTIPY_REDIRECT_URI')
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(redirect_uri=uri,
                              client_id=client_id,
                              client_secret=client_secret,
                              scope="playlist-modify-private"))


def get_uri_song(song_name, artist, year):
    try:
        song_uri = sp.search(q=f"track:{song_name} artist:{artist}",
                             type='track')['tracks']['items'][0]['uri']
        return song_uri
    except IndexError:
        try:
            song_uri = sp.search(q=f"track:{song_name} year:{year}",
                                 type='track')['tracks']['items'][0]['uri']
            return song_uri
        except IndexError:
            print(
                f"{song_name} by {artist} doesn't exist in Spotify. Skipped.")


str_date = input(
    "Which year do you want to travel to? Type the date in this format YYYY-MM-DD:\n "
)
str_year = str_date.split('-')[0]
response = req.get(f"https://www.billboard.com/charts/hot-100/{str_date}")
web_page = response.text
soup = BeautifulSoup(web_page, 'html.parser')

song_tags = soup.find_all(
    "span",
    class_="chart-element__information__song text--truncate color--primary")
artist_tags = soup.find_all(
    "span",
    class_="chart-element__information__artist text--truncate color--secondary"
)

artists = [tag.getText() for tag in artist_tags]
songs = [tag.getText() for tag in song_tags]

song_artist = []
for index in range(len(songs) - 1):
    song_artist.append({'song': songs[index], 'artist': artists[index]})

songs_uris = [
    get_uri_song(values['song'].replace("'", ""),
                 values['artist'].split(' Feat')[0].strip(), str_year)
    for values in song_artist
]

user_id = sp.current_user()["id"]
playlist = sp.user_playlist_create(user=user_id,
                                   name=f"{str_date} Billboard 100",
                                   public=False,
                                   collaborative=False)

songs_uris = [uri for uri in songs_uris if uri is not None]
sp.playlist_add_items(playlist_id=playlist["id"], items=songs_uris)
