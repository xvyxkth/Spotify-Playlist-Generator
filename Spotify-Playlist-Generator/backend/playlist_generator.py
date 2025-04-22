import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth

scope = 'playlist-modify-public'
username = 'cafkj0uiiuh5rx6jzdsrz5yrc'
client_id = '28f99ce226a84d5abcbcd0573cb09c03'
client_secret = '05aec2de3861479f873448f7beecf30e'

token = SpotifyOAuth(
    scope = scope, 
    client_id = client_id, 
    client_secret = client_secret, 
    redirect_uri = "https://example.com/callback"
    )

spotifyObject = spotipy.Spotify(auth_manager = token)

def create_playlist(playlist_name = "New Playlist", playlist_description = "Playlist Description"):

    # Create the Playlist
    playlist = spotifyObject.user_playlist_create(
        user = username, 
        name = playlist_name, 
        public = True,
        description = playlist_description
    )

    return playlist
    
def add_songs(tracks, playlist):

    # Find the URI of the recommended songs
    tracks_uri = []
    for track_id, track_name in tracks.items():
        searchResult = spotifyObject.search(q = track_name)
        for i in range(len(searchResult['tracks']['items'])):
            if (searchResult['tracks']['items'][i]['id'] == track_id):
                tracks_uri.append(searchResult['tracks']['items'][i]['uri'])

    # Get the Playlist ID of the playlist that you created
    playlist_id = playlist['id']

    # # Add the songs
    spotifyObject.user_playlist_add_tracks(user = username, playlist_id = playlist_id, tracks = tracks_uri)

# Uncomment main() when you are trying to run this file on terminal
# def main():

#     # Take User Input
#     playlist_name = input("Enter a Playlist Name : ")
#     playlist_description = input("Enter the Description of your Playlist : ")

#     # # Create the Playlist
#     playlist = create_playlist(playlist_name, playlist_description)

    # Get the recommended tracks here
    # An example of recommended tracks
    # recommended_tracks = {'75FpbthrwQmzHlBJLuGdC7': 'Call You Mine - Keanu Silva Remix',
    #                       '2OAylPUDDfwRGfe0lYqlCQ': 'Never Really Over - R3HAB Remix',
    #                       '6b1RNvAcJjQH73eZO4BLAB': 'Post Malone (feat. RANI) - GATTÜSO Remix',
    #                       '7bF6tCO3gFb8INrEDcjNT5': 'Tough Love - Tiësto Remix / Radio Edit',
    #                       '1IXGILkPm0tOCNeq00kCPa': "If I Can't Have You - Gryffin Remix"
    #                      }
    
    # Add recommended tracks to the playlist
#     add_songs(recommended_tracks, playlist)

# main()