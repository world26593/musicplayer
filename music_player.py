import streamlit as st
import yt_dlp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set up page configuration
st.set_page_config(page_title="Streamlit YouTube Music Player 🎶", layout="centered")
st.title("🎵 YouTube Music Player (With ML Recommender)")

# Dark Mode toggle
dark_mode = st.sidebar.checkbox("Dark Mode", value=False)
if dark_mode:
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )

query = st.text_input("Enter a song name or artist", "")

if 'history' not in st.session_state:
    st.session_state.history = []

if 'favorites' not in st.session_state:
    st.session_state.favorites = []

# ML-Based Recommendation Engine
def recommend_tracks(user_input, history):
    if not history:
        return []

    corpus = history + [user_input]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)

    sim_matrix = cosine_similarity(X[-1], X[:-1])
    similar_indices = sim_matrix.argsort()[0][-3:][::-1]

    return [history[i] for i in similar_indices if corpus[i] != user_input]

# YouTube search
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
            videos.append({
                'title': entry['title'],
                'video_id': entry['id'],
                'duration': entry.get('duration', 'N/A'),
                'thumbnail': entry.get('thumbnail', '')
            })
    return videos

# Handle search
if st.button("Search") and query:
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    videos = get_videos(query)
    for v in videos:
        st.subheader(f"{v['title']} ({v['duration']})")
        if v['thumbnail']:
            st.image(v['thumbnail'], width=300)
        st.video(f"https://www.youtube.com/embed/{v['video_id']}")

        if st.button(f"Add {v['title']} to Favorites"):
            if v['title'] not in [f['title'] for f in st.session_state.favorites]:
                st.session_state.favorites.append(v)

    # Show recommendations
    st.subheader("🔁 Recommended for You:")
    recommendations = recommend_tracks(query, st.session_state.history[:-1])
    for rec in recommendations:
        st.markdown(f"🎧 {rec}")

# Sidebar: history, favorites, queue
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
    for q in st.session_state.history[1:]:
        st.sidebar.write(q)
