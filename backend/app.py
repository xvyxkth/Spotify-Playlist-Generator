from flask import Flask, request, jsonify
import subprocess
import json
import os
import re
from flask_cors import CORS
import pandas as pd
from dotenv import load_dotenv
import numpy as np # Import numpy to handle NaN values

# Load environment variables (ensure this path is correct for your .env file)
dotenv_path = '/path/to/your/.env/file' # Make sure this is correct for app.py
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__)
CORS(app)

# Define the authorization callback URL - Still recommend removing this hardcoding for actual production
AUTH_CALLBACK_URL = "https://example.com/callback?code=AQAviYmyik5-R-rX00OR6715lGICl0Bwm-nKCMpoJuH4oVhk8Q5Tow48gcq-OMWLUfvw9gykWhFrxNUYyED3cF8nzmGoj0sj7bh8qBM5yixONMLVyjOtwYXqIcxIuXmjmOpDd7qbOyZgBQa387Lfc99Pbw46bynMh8t4MJQrEx4XBXEesC9N_x-tlhAROyUV9a4N5TOWqDE"

# Define the path to your CSV file relative to app.py
# Adjust this path based on your project structure
csv_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'spotify_songs.csv')
# For example, if it's in the parent directory of backend:
# csv_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spotify_songs.csv')


@app.route('/api/songs', methods=['GET'])
def get_songs_list():
    try:
        df = pd.read_csv(csv_file_path)

        # IMPORTANT FIX: Replace NaN values with None
        # .replace({np.nan: None}) will replace all NaN values across the DataFrame
        # or you can specify columns: df[['track_artist', 'track_name']].replace({np.nan: None})
        # For simplicity and robustness, replacing all NaNs with None is often fine for JSON export.
        df = df.replace({np.nan: None})

        # Select only the necessary columns
        songs_list = df[['track_id', 'track_name', 'track_artist']].to_dict(orient='records')

        return jsonify(songs_list)
    except FileNotFoundError:
        return jsonify({'error': f'spotify_songs.csv not found at {csv_file_path}. Absolute path attempted: {os.path.abspath(csv_file_path)}'}), 404
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'spotify_songs.csv is empty.'}), 400
    except Exception as e:
        import traceback
        print("Error loading songs:", str(e))
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to load songs list: {str(e)}'}), 500


@app.route('/api/recommend', methods=['POST'])
def recommend():
    # ... (this part of your app.py remains unchanged) ...
    try:
        data = request.json
        selected_songs_data = data.get('songs', [])
        playlist_name = data.get('playlistName', 'Recommended Playlist')
        playlist_description = data.get('playlistDescription', 'Auto-generated playlist using recommendation algorithm')

        songs_for_algo = [song_obj['track_name'] for song_obj in selected_songs_data]

        parameters = {
            'songs': songs_for_algo,
            'playlist_name': playlist_name,
            'playlist_description': playlist_description,
            'auth_callback_url': AUTH_CALLBACK_URL
        }

        with open('notebook_parameters.json', 'w') as f:
            json.dump(parameters, f)

        with open('Recommendation_Algo.ipynb', 'r') as f:
            notebook_content = json.load(f)

        parameter_cell = {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "source": [
                "# Load parameters from JSON file\n",
                "import json\n",
                "with open('notebook_parameters.json', 'r') as f:\n",
                "    parameters = json.load(f)\n",
                "\n",
                "# Extract parameters\n",
                "songs = parameters['songs']\n",
                "playlist_name = parameters['playlist_name']\n",
                "playlist_description = parameters['playlist_description']\n",
                "auth_callback_url = parameters['auth_callback_url']\n",
                "\n",
                "# Monkey patch the input function to return the auth URL when needed\n",
                "original_input = input\n",
                "\n",
                "def patched_input(prompt=''):\n",
                "    print(f\"Input requested: {prompt}\")\n",
                "    if 'url' in prompt.lower() or 'callback' in prompt.lower() or 'http' in prompt.lower():\n",
                "        print(f\"Automatically providing auth callback URL: {auth_callback_url}\")\n",
                "        return auth_callback_url\n",
                "    return 'default_input'\n",
                "\n",
                "import builtins\n",
                "builtins.input = patched_input\n",
                "try:\n",
                "    builtins.raw_input = patched_input\n",
                "except AttributeError:\n",
                "    pass\n",
                "\n",
                "print(f\"Loaded parameters: {len(songs)} songs, playlist name: {playlist_name}\")\n"
            ],
            "outputs": []
        }

        notebook_content['cells'].insert(0, parameter_cell)

        with open('Recommendation_Algo_with_params.ipynb', 'w') as f:
            json.dump(notebook_content, f)

        result = subprocess.run(
            [
                'jupyter', 'nbconvert',
                '--to', 'notebook',
                '--execute',
                'Recommendation_Algo_with_params.ipynb',
                '--output', 'Recommendation_Algo_executed.ipynb',
                '--ExecutePreprocessor.kernel_name=myenv',
                '--ExecutePreprocessor.timeout=-1'
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("Notebook execution failed:", result.stderr)
            return jsonify({
                'success': False,
                'message': 'Failed to execute recommendation algorithm',
                'error': result.stderr
            }), 500

        return jsonify({
            'success': True,
            'message': f'Playlist "{playlist_name}" created successfully!'
        })

    except Exception as e:
        import traceback
        print("Error:", str(e))
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'An error occurred',
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)