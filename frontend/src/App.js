import React, { useState, useEffect } from 'react';
import Select from 'react-select'
import './App.css';

function App() {
  const [songs, setSongs] = useState([]); // List of songs ADDED to the playlist
  const [availableSongs, setAvailableSongs] = useState([]); // List of songs from CSV for dropdown
  const [selectedDropdownSong, setSelectedDropdownSong] = useState(''); // Currently selected song in the dropdown
  const [playlistName, setPlaylistName] = useState('');
  const [playlistDescription, setPlaylistDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); // 'success', 'error', 'info'

  const availableSongsOptions = availableSongs.map(song => ({
    value: song.track_id,
    label: `${song.track_name} - ${song.track_artist}`,
    // You can also store the full song object here if needed later
    songData: song
  }));

  // --- New useEffect to fetch available songs from backend ---
  useEffect(() => {
    const fetchAvailableSongs = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/songs');
        console.log("The response is : " + response.ok);
        const data = await response.json();
        if (response.ok) {
          setAvailableSongs(data);
          // Set initial selected song if there are any
          if (data.length > 0) {
            setSelectedDropdownSong(data[0].track_id); // Select the first song by default
          }
        } else {
          setMessage(data.error || 'Failed to load available songs.');
          setMessageType('error');
        }
      } catch (error) {
        setMessage('Error fetching available songs from server.');
        setMessageType('error');
        console.error('Error fetching available songs:', error);
      }
    };
    fetchAvailableSongs();
  }, []); // Empty dependency array means this runs once on component mount

  const handleAddSong = () => {
    if (selectedDropdownSong) {
      // Find the full song object from availableSongs based on the selected track_id
      const songToAdd = availableSongs.find(
        (song) => song.track_id === selectedDropdownSong
      );

      if (songToAdd && !songs.some(s => s.track_id === songToAdd.track_id)) { // Prevent duplicates
        setSongs([...songs, songToAdd]);
        // Optional: Reset dropdown to default or clear selection after adding
        // setSelectedDropdownSong('');
      } else if (songs.some(s => s.track_id === songToAdd.track_id)) {
        setMessage('Song already added to the list!');
        setMessageType('info');
      }
    } else {
      setMessage('Please select a song from the dropdown.');
      setMessageType('error');
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

      // Prepare songs data to send to backend: track_name and track_id (if your algo needs it)
      // Sending an array of objects like {track_id, track_name, track_artist} is robust
      const songsToSend = songs.map(song => ({
        track_id: song.track_id,
        track_name: song.track_name,
        track_artist: song.track_artist // Include artist if backend needs it or for debugging
      }));

      const response = await fetch('http://127.0.0.1:5000/api/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          songs: songsToSend, // Send the list of selected song objects
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
              placeholder="Enter Playlist Name"
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
            {/* Replace text input with select dropdown */}
            <Select
              options={availableSongsOptions}
              value={availableSongsOptions.find(option => option.value === selectedDropdownSong)}
              onChange={(selectedOption) => {
                setSelectedDropdownSong(selectedOption ? selectedOption.value : '');
              }}
              placeholder="-- Select a song --"
              isClearable={true} // Allows clearing the selection
              isDisabled={availableSongs.length === 0}
              // You can pass styles to customize its appearance further
              styles={{
                control: (baseStyles) => ({
                  ...baseStyles,
                  backgroundColor: '#333333',
                  borderColor: '#404040',
                  color: '#FFFFFF',
                  padding: '4px', // Adjust padding if needed
                  borderRadius: '6px',
                  '&:hover': {
                    borderColor: '#1DB954',
                  },
                  boxShadow: 'none', // Remove default focus shadow if you prefer custom
                }),
                singleValue: (baseStyles) => ({
                  ...baseStyles,
                  color: '#FFFFFF',
                }),
                input: (baseStyles) => ({
                  ...baseStyles,
                  color: '#FFFFFF', // Text color when typing/selecting
                }),
                placeholder: (baseStyles) => ({
                  ...baseStyles,
                  color: '#A0A0A0', // Placeholder text color
                }),
                menu: (baseStyles) => ({
                  ...baseStyles,
                  backgroundColor: '#282828', // Background of the dropdown menu
                  borderRadius: '8px',
                  zIndex: 100, // Ensure it's above other elements
                }),
                option: (baseStyles, state) => ({
                  ...baseStyles,
                  backgroundColor: state.isFocused ? '#1DB954' : (state.isSelected ? '#169c46' : '#282828'),
                  color: '#E0E0E0',
                  '&:active': {
                    backgroundColor: '#169c46',
                  },
                }),
                // Add more styles for other parts if necessary (e.g., dropdown indicator, clear indicator)
              }}
            />
            <button
              onClick={handleAddSong}
              disabled={!selectedDropdownSong || isSubmitting}
            >
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
                  {/* Display name and artist for added songs */}
                  {`${song.track_name} - ${song.track_artist}`}
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