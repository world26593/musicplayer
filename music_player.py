import streamlit as st
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# ---------------------------- Spotify Setup ----------------------------
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="YOUR_SPOTIFY_CLIENT_ID",        # 🔐 Replace with your Spotify Client ID
    client_secret="YOUR_SPOTIFY_CLIENT_SECRET" # 🔐 Replace with your Spotify Client Secret
))

# -------------------------- Streamlit Setup ----------------------------
st.set_page_config(page_title="Streamlit YouTube Music Player 🎶", layout="centered")
st.title("🎵 YouTube Music Player (With ML Recommender)")

# ---------------------- Dark Mode Toggle -------------------------------
dark_mode = st.sidebar.checkbox("Dark Mode", value=False)
if dark_mode:
    st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: white;
    }
    .streamlit-expanderHeader {
        background-color: #333333;
    }
    .streamlit-expanderContent {
        background-color: #222222;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------ Session State Initialization -----------------------
if 'history' not in st.session_state:
    st.session_state.history = []

if 'favorites' not in st.session_state:
    st.session_state.favorites = []

if 'features' not in st.session_state:
    st.session_state.features = []

# ------------------- Get YouTube Videos -------------------------------
def get_videos(search_term, max_results=5):
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'extract_flat': True,
        'limit': max_results
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{search_term}", download=False)
        videos = []
        for entry in result['entries']:
            title = entry['title']
            video_id = entry['id']
            duration = entry.get('duration', 'N/A')
            thumbnail = entry.get('thumbnail', '')
            videos.append({
                'title': title,
                'video_id': video_id,
                'duration': duration,
                'thumbnail': thumbnail
            })
    return videos

# ------------------- Get Spotify Audio Features ------------------------
def get_track_features(track_name):
    results = sp.search(q=track_name, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        features = sp.audio_features([track['id']])[0]
        metadata = {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'id': track['id'],
            'popularity': track['popularity'],
            'url': track['external_urls']['spotify'],
        }
        return {**metadata, **features}
    return None

# --------------------- Recommend Songs ---------------------------------
def recommend_from_history(k=3):
    df = pd.DataFrame(st.session_state.features)
    if df.empty:
        return []
    audio_features = ['danceability', 'energy', 'loudness', 'valence', 'tempo']
    X = df[audio_features]
    last_vec = X.iloc[-1].values.reshape(1, -1)
    similarity = cosine_similarity(last_vec, X).flatten()
    df['similarity'] = similarity
    top = df.sort_values(by='similarity', ascending=False).iloc[1:k+1]
    return top.to_dict('records')

# ------------------------ Main Input UI --------------------------------
query = st.text_input("Enter a song name or artist", "")

# ------------------------ Search Handler -------------------------------
if st.button("Search") and query:
    # Add to history
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    # Save Spotify features
    feature_data = get_track_features(query)
    if feature_data:
        st.session_state.features.append(feature_data)

    # Fetch YouTube videos
    videos = get_videos(query)

    # Show Videos
    for v in videos:
        st.subheader(f"{v['title']} ({v['duration']})")
        if v['thumbnail']:
            st.image(v['thumbnail'], width=300)
        else:
            st.warning("No thumbnail available.")
        st.video(f"https://www.youtube.com/embed/{v['video_id']}")

        if st.button(f"Add {v['title']} to Favorites"):
            if v['title'] not in [f['title'] for f in st.session_state.favorites]:
                st.session_state.favorites.append(v)

    # Show Recommendations
    st.subheader("🧠 ML-Based Recommendations")
    recs = recommend_from_history()
    for rec in recs:
        st.markdown(f"**{rec['name']}** by *{rec['artist']}*")
        st.markdown(f"[Listen on Spotify]({rec['url']})")

# ------------------ Sidebar History, Favorites, Queue ------------------
if st.session_state.history:
    st.sidebar.subheader("Search History")
    for q in st.session_state.history:
        st.sidebar.write(q)

if st.session_state.favorites:
    st.sidebar.subheader("Favorite Songs")
    for f in st.session_state.favorites:
        st.sidebar.write(f"{f['title']}")

if len(st.session_state.history) > 1:
    st.sidebar.subheader("Autoplay Queue")
    queue = st.session_state.history[1:]
    for q in queue:
        st.sidebar.write(q)
