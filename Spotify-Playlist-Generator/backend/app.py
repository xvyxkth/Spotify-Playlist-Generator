# app.py
from flask import Flask, request, jsonify
import subprocess
import json
import os
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define the authorization callback URL
AUTH_CALLBACK_URL = "https://example.com/callback?code=AQAviYmyik5-R-rX00OR6715lGICl0Bwm-nKCMpoJuH4oVhk8Q5Tow48gcq-OMWLUfvw9gykWhFrxNUYyED3cF8nzmGoj0sj7bh8qBM5yixONMLVyjOtwYXqIcxIuXmjmOpDd7qbOyZgBQa387Lfc99Pbw46bynMh8t4MJQrEx4XBXEesC9N_x-tlhAROyUV9a4N5TOWqDE"

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        # Get the songs from the request
        data = request.json
        songs = data.get('songs', [])
        playlist_name = data.get('playlistName', 'Recommended Playlist')
        playlist_description = data.get('playlistDescription', 'Auto-generated playlist using recommendation algorithm')
        
        # Save the parameters to a JSON file that can be read by the notebook
        parameters = {
            'songs': songs,
            'playlist_name': playlist_name,
            'playlist_description': playlist_description,
            'auth_callback_url': AUTH_CALLBACK_URL
        }
        
        with open('notebook_parameters.json', 'w') as f:
            json.dump(parameters, f)
        
        # Create a temporary notebook with parameters injection and input patching
        with open('Recommendation_Algo.ipynb', 'r') as f:
            notebook_content = json.load(f)
        
        # Add a cell at the beginning to load parameters
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
                "    # If this looks like it's asking for the auth callback URL\n",
                "    if 'url' in prompt.lower() or 'callback' in prompt.lower() or 'http' in prompt.lower():\n",
                "        print(f\"Automatically providing auth callback URL: {auth_callback_url}\")\n",
                "        return auth_callback_url\n",
                "    # For any other input request, just return a default value\n",
                "    return 'default_input'\n",
                "\n",
                "# Replace the built-in input function with our patched version\n",
                "import builtins\n",
                "builtins.input = patched_input\n",
                "# Also patch raw_input for Python 2 compatibility\n",
                "try:\n",
                "    builtins.raw_input = patched_input\n",
                "except AttributeError:\n",
                "    pass\n",
                "\n",
                "print(f\"Loaded parameters: {len(songs)} songs, playlist name: {playlist_name}\")\n"
            ],
            "outputs": []
        }
        
        # Insert the cell at the beginning of the notebook
        notebook_content['cells'].insert(0, parameter_cell)
        
        # Save the modified notebook
        with open('Recommendation_Algo_with_params.ipynb', 'w') as f:
            json.dump(notebook_content, f)
        
        # Execute the modified notebook
        result = subprocess.run(
            [
                'jupyter', 'nbconvert', 
                '--to', 'notebook', 
                '--execute', 
                'Recommendation_Algo_with_params.ipynb', 
                '--output', 'Recommendation_Algo_executed.ipynb',
                '--ExecutePreprocessor.kernel_name=python3',
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
        
        # If we get here, the playlist was created successfully
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