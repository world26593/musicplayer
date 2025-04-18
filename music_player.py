import streamlit as st
import yt_dlp

# Set up page configuration
st.set_page_config(page_title="Streamlit YouTube Music Player 🎶", layout="centered")

# Title
st.title("🎵 YouTube Music Player (Enhanced)")

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

# Input for song or artist
query = st.text_input("Enter a song name or artist", "")

# Initialize session state for history and favorites
if 'history' not in st.session_state:
    st.session_state.history = []

if 'favorites' not in st.session_state:
    st.session_state.favorites = []


# Function to get videos from YouTube search using yt-dlp
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


# Handle search button click
if st.button("Search") and query:
    # Add search term to history
    if query not in st.session_state.history:
        st.session_state.history.append(query)

    # Fetch videos
    videos = get_videos(query)

    # Display videos
    for v in videos:
        st.subheader(f"{v['title']} ({v['duration']})")

        # Only display thumbnail if it's not empty
        if v['thumbnail']:
            st.image(v['thumbnail'], width=300)
        else:
            st.warning("No thumbnail available.")

        st.video(f"https://www.youtube.com/embed/{v['video_id']}")

        # Option to save to favorites
        if st.button(f"Add {v['title']} to Favorites"):
            if v['title'] not in [f['title'] for f in st.session_state.favorites]:
                st.session_state.favorites.append(v)

# Display search history
if st.session_state.history:
    st.sidebar.subheader("Search History")
    for query in st.session_state.history:
        st.sidebar.write(query)

# Display favorite songs
if st.session_state.favorites:
    st.sidebar.subheader("Favorite Songs")
    for f in st.session_state.favorites:
        st.sidebar.write(f"{f['title']}")

# Display autoplay queue
if len(st.session_state.history) > 1:
    st.sidebar.subheader("Autoplay Queue")
    queue = st.session_state.history[1:]  # The queue starts from the 2nd search onward
    for q in queue:
        st.sidebar.write(q)
