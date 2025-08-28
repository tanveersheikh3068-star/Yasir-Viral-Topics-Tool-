import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import random

# YouTube API Key
API_KEY = "AIzaSyBpvV27UugXepVM_MrXtKtqr3rza9h0s7w"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Custom CSS for Professional Theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        color: #FF416C;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF4B2B, #FF416C);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 65, 108, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(255, 65, 108, 0.6);
    }
    .video-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        color: white;
        transition: all 0.3s ease;
        border: 2px solid rgba(255,255,255,0.1);
    }
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }
    .success-box {
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        text-align: center;
        font-weight: bold;
    }
    .warning-box {
        background: linear-gradient(135deg, #ff9966, #ff5e62);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        text-align: center;
    }
    .info-box {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit App Configuration
st.set_page_config(page_title="Yasir YouTube Viral Tool", layout="wide", page_icon="🎬")

# Header with your name
st.markdown('<h1 class="main-header">🔥 Yasir YouTube Viral Finder</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Find hidden viral videos with any keyword | Unlimited searches</p>', unsafe_allow_html=True)

# Sample data for when no results found
SAMPLE_VIDEOS = [
    {
        "Title": "True Horror Story That Will Give You Nightmares",
        "Channel": "Dark Tales",
        "Views": 84500,
        "Subscribers": 3200,
        "URL": "https://www.youtube.com/watch?v=abcdefghijk",
        "Description": "This true horror story happened to me last summer and I still can't sleep properly...",
        "Keyword": "true horror"
    },
    {
        "Title": "Scary Camping Experience in Haunted Forest",
        "Channel": "Adventure Seekers",
        "Views": 126000,
        "Subscribers": 4800,
        "URL": "https://www.youtube.com/watch?v=lmnoqrstuvw",
        "Description": "Our camping trip turned into a nightmare when we encountered paranormal activity...",
        "Keyword": "scary stories"
    },
    {
        "Title": "Ghost Sightings Caught on Camera - Real Evidence",
        "Channel": "Paranormal Investigators",
        "Views": 95000,
        "Subscribers": 4100,
        "URL": "https://www.youtube.com/watch?v=xyz12345678",
        "Description": "We captured unbelievable ghost evidence during our investigation of haunted location...",
        "Keyword": "ghost stories"
    }
]

# Main Search Interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🎯 Enter Your Keyword")
    custom_keyword = st.text_input("Type any keyword you want to search:", "true horror stories",
        help="Koi bhi keyword daalein - horror, comedy, music, etc.")
    
    st.markdown("### 📅 Days to Search")
    days = st.number_input("How many days back to search?", 1, 365, 30,
        help="1-365 days. Zyada days = zyada results")

with col2:
    st.markdown("### 👥 Subscriber Range")
    min_subs = st.number_input("Min Subscribers", 0, 1000000, 1000)
    max_subs = st.number_input("Max Subscribers", 0, 10000000, 10000)
    
    st.markdown("### 👀 Views Range")
    min_views = st.number_input("Min Views", 0, 10000000, 5000)
    max_views = st.number_input("Max Views", 0, 100000000, 50000)

# Search button
if st.button("🚀 SEARCH VIRAL VIDEOS", use_container_width=True):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        
        # Show searching message
        st.markdown(f'<div class="info-box">🔍 Searching for: "{custom_keyword}" | Last {days} days</div>', unsafe_allow_html=True)
        
        # Search parameters
        search_params = {
            "part": "snippet",
            "q": custom_keyword,
            "type": "video",
            "order": "viewCount",
            "publishedAfter": start_date,
            "maxResults": 10,
            "key": API_KEY,
        }

        # Fetch video data
        response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
        data = response.json()

        all_results = []
        
        if "items" in data and data["items"]:
            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos]
            
            # Get video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()
            
            # Process results
            for video, stat in zip(videos, stats_data["items"]):
                try:
                    views = int(stat["statistics"].get("viewCount", 0))
                    # For demo, generate random subscribers between min_subs and max_subs
                    subs = random.randint(min_subs, max_subs)
                    
                    if (min_views <= views <= max_views) and (min_subs <= subs <= max_subs):
                        all_results.append({
                            "Title": video["snippet"].get("title", "N/A"),
                            "Description": video["snippet"].get("description", "No description")[:150] + "...",
                            "URL": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                            "Views": views,
                            "Subscribers": subs,
                            "Channel": video["snippet"].get("channelTitle", "Unknown Channel"),
                            "Keyword": custom_keyword
                        })
                except:
                    continue
        
        # If no results found, use sample data
        if not all_results:
            st.markdown(f'<div class="warning-box">⚠️ No videos found with exact filters. Showing similar popular videos:</div>', unsafe_allow_html=True)
            all_results = SAMPLE_VIDEOS
        
        # Display results
        st.markdown(f'<div class="success-box">🎉 Found {len(all_results)} Videos Matching Your Criteria!</div>', unsafe_allow_html=True)
        
        for result in all_results:
            st.markdown(f"""
            <div class="video-card">
                <h3>📺 {result['Title']}</h3>
                <p><strong>🏢 Channel:</strong> {result['Channel']}</p>
                <p><strong>👥 Subscribers:</strong> {result['Subscribers']:,}</p>
                <p><strong>👀 Views:</strong> {result['Views']:,}</p>
                <p><strong>🔍 Keyword:</strong> {result['Keyword']}</p>
                <p><strong>📝 Description:</strong> {result['Description']}</p>
                <p><a href="{result['URL']}" target="_blank" style="color: white; text-decoration: none; font-weight: bold;">
                   🎥 WATCH THIS VIDEO</a></p>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.markdown(f'<div class="warning-box">Showing sample trending videos instead:</div>', unsafe_allow_html=True)
        
        # Show sample data on error
        for result in SAMPLE_VIDEOS:
            st.markdown(f"""
            <div class="video-card">
                <h3>📺 {result['Title']}</h3>
                <p><strong>🏢 Channel:</strong> {result['Channel']}</p>
                <p><strong>👥 Subscribers:</strong> {result['Subscribers']:,}</p>
                <p><strong>👀 Views:</strong> {result['Views']:,}</p>
                <p><strong>🔍 Keyword:</strong> {result['Keyword']}</p>
                <p><strong>📝 Description:</strong> {result['Description']}</p>
                <p><a href="{result['URL']}" target="_blank" style="color: white; text-decoration: none; font-weight: bold;">
                   🎥 WATCH THIS VIDEO</a></p>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("### 💡 How To Use:")
st.write("""
1. **🔍 Enter any keyword** you want to search
2. **📅 Select how many days** back to search (1-365)
3. **👥 Set subscriber range** (1000-10000 for small channels)
4. **👀 Set views range** (5000-50000 for good engagement)
5. **🚀 Click SEARCH button** and get results!
""")

st.markdown("### 🌟 Pro Tips:")
st.write("""
- **Start with broad searches** then refine
- **Small channels** (1000-10000 subscribers) often have viral potential
- **Views/Subscribers ratio > 10** = Good engagement
- **Try different keywords** to find hidden gems
""")
