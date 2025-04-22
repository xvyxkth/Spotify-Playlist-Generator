// App.js
import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [songs, setSongs] = useState([]);
  const [currentSong, setCurrentSong] = useState('');
  const [playlistName, setPlaylistName] = useState('');
  const [playlistDescription, setPlaylistDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success' or 'error'

  const handleAddSong = () => {
    if (currentSong.trim() !== '') {
      setSongs([...songs, currentSong.trim()]);
      setCurrentSong('');
    }
  };

  const handleRemoveSong = (index) => {
    const updatedSongs = [...songs];
    updatedSongs.splice(index, 1);
    setSongs(updatedSongs);
  };

  const handleCreatePlaylist = async () => {
    if (songs.length === 0) {
      setMessage('Please add at least one song.');
      setMessageType('error');
      return;
    }

    try {
      setIsSubmitting(true);
      setMessage('Creating playlist... This may take a moment.');
      setMessageType('info');

      const response = await fetch('http://127.0.0.1:5000/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          songs: songs,
          playlistName: playlistName || 'Recommended Playlist',
          playlistDescription: playlistDescription || 'Auto-generated playlist using recommendation algorithm'
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setMessage(data.message);
        setMessageType('success');
        // Reset form after successful submission
        setSongs([]);
        setPlaylistName('');
        setPlaylistDescription('');
      } else {
        setMessage(data.message || 'Failed to create playlist.');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('Error connecting to the server. Please try again later.');
      setMessageType('error');
      console.error('Error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Mood-Based Spotify Playlist Generator</h1>
        <h3>Simply enter the songs that you are in the mood to listen to and we'll generate a spotify playlist of songs that give off the same vibes</h3>
      </header>

      <main>
        <div className="form-section">
          <h2>Playlist Details</h2>
          <div className="form-group">
            <label htmlFor="playlist-name">Playlist Name:</label>
            <input
              type="text"
              id="playlist-name"
              value={playlistName}
              onChange={(e) => setPlaylistName(e.target.value)}
              placeholder="My Awesome Playlist"
            />
          </div>

          <div className="form-group">
            <label htmlFor="playlist-description">Playlist Description:</label>
            <textarea
              id="playlist-description"
              value={playlistDescription}
              onChange={(e) => setPlaylistDescription(e.target.value)}
              placeholder="A collection of songs I love and recommendations based on them."
            />
          </div>
        </div>

        <div className="form-section">
          <h2>Add Songs</h2>
          <div className="song-input">
            <input
              type="text"
              value={currentSong}
              onChange={(e) => setCurrentSong(e.target.value)}
              placeholder="Enter a song title or artist - song"
              onKeyPress={(e) => e.key === 'Enter' && handleAddSong()}
            />
            <button onClick={handleAddSong} disabled={!currentSong.trim()}>
              Add Song
            </button>
          </div>
        </div>

        <div className="songs-list">
          <h3>Songs ({songs.length})</h3>
          {songs.length > 0 ? (
            <ul>
              {songs.map((song, index) => (
                <li key={index}>
                  {song}
                  <button 
                    className="remove-button"
                    onClick={() => handleRemoveSong(index)}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-message">No songs added yet.</p>
          )}
        </div>

        {message && (
          <div className={`message ${messageType}`}>
            {message}
          </div>
        )}

        <div className="submit-section">
          <button 
            className="create-button"
            onClick={handleCreatePlaylist}
            disabled={isSubmitting || songs.length === 0}
          >
            {isSubmitting ? 'Creating...' : 'Create Playlist'}
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;