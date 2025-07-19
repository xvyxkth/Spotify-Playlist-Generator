import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv # Import load_dotenv

# --- Add this section at the very beginning ---
# Get the absolute path to your .env file
# Replace 'path/to/your/.env/file' with the actual absolute path
# For example, if your .env is in your home directory, it might be:
# dotenv_path = os.path.join(os.path.expanduser('~'), '.env')
# If it's in a specific global directory, provide the full path:
dotenv_path = '../.env'
load_dotenv(dotenv_path=dotenv_path)
# --- End of added section ---

# Now, os.getenv() will be able to retrieve the variables
scope = 'playlist-modify-public user-library-read'
username = os.getenv("CLIENT_USERNAME") # Ensure this is also in your .env if used
client_id = os.getenv("SPOTIPY_CLIENT_ID") # Spotipy looks for SPOTIPY_CLIENT_ID/SECRET by default
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET") # Spotipy looks for SPOTIPY_CLIENT_ID/SECRET by default

# It's good practice to add checks to ensure variables are loaded
if not client_id:
    raise ValueError("SPOTIPY_CLIENT_ID environment variable not set.")
if not client_secret:
    raise ValueError("SPOTIPY_CLIENT_SECRET environment variable not set.")

# IMPORTANT: Use the exact redirect_uri you configured in your Spotify Developer Dashboard
redirect_uri = "http://localhost:8888/callback" # THIS MUST MATCH YOUR SPOTIFY APP SETTINGS!

token_manager = SpotifyOAuth(
    scope=scope,
    client_id=client_id, # Use the variables explicitly loaded
    client_secret=client_secret, # Use the variables explicitly loaded
    redirect_uri=redirect_uri,
    cache_path=".cache"
)

spotifyObject = spotipy.Spotify(auth_manager=token_manager)

# ... (rest of your code remains the same) ...

def create_playlist(playlist_name="New Playlist", playlist_description="Playlist Description"):
    # Create the Playlist
    user_id = spotifyObject.current_user()['id']
    playlist = spotifyObject.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=True,
        description=playlist_description
    )
    return playlist

def add_songs(tracks, playlist):
    tracks_uri = []
    for track_id, track_name in tracks.items():
        tracks_uri.append(f"spotify:track:{track_id}")

    playlist_id = playlist['id']
    spotifyObject.user_playlist_add_tracks(user=spotifyObject.current_user()['id'], playlist_id=playlist_id, tracks=tracks_uri)

def main():
    print("Initiating Spotify Authorization Flow...")
    print("Authorization successful! You can now proceed.")

    playlist_name = input("Enter a Playlist Name: ")
    playlist_description = input("Enter the Description of your Playlist: ")

    playlist = create_playlist(playlist_name, playlist_description)
    print(f"Playlist '{playlist_name}' created with ID: {playlist['id']}")

    recommended_tracks = {'75FpbthrwQmzHlBJLuGdC7': 'Call You Mine - Keanu Silva Remix',
                          '2OAylPUDDfwRGfe0lYqlCQ': 'Never Really Over - R3HAB Remix',
                          '6b1RNvAcJjQH73eZO4BLAB': 'Post Malone (feat. RANI) - GATTÜSO Remix',
                          '7bF6tCO3gFb8INrEDcjNT5': 'Tough Love - Tiësto Remix / Radio Edit',
                          '1IXGILkPm0tOCNeq00kCPa': "If I Can't Have You - Gryffin Remix"
                         }

    add_songs(recommended_tracks, playlist)
    print("Songs added to the playlist.")

if __name__ == "__main__":
    main()