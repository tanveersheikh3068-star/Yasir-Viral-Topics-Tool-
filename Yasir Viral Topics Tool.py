import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import base64
import json

# YouTube API Key - Aap ki key yahan add kar di hai
API_KEY = "AIzaSyBpvV27UugXepVM_MrXtKtqr3rza9h0s7w"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Custom CSS for Blue Theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(45deg, #1E90FF, #4169E1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #4169E1;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(45deg, #1E90FF, #4169E1);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(65, 105, 225, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(65, 105, 225, 0.6);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #000080, #1E90FF);
        color: white;
    }
    .stNumberInput, .stTextInput, .stSelectbox, .stSlider {
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 1rem;
    }
    .stExpander {
        background: linear-gradient(135deg, #1E90FF 0%, #000080 100%);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        border: none;
        color: white;
    }
    .success-message {
        background: linear-gradient(135deg, #1E90FF, #00BFFF);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .video-card {
        background: linear-gradient(135deg, #1E90FF 0%, #000080 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        color: white;
        transition: all 0.3s ease;
    }
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }
    .tab-content {
        padding: 15px;
        background: rgba(30, 144, 255, 0.1);
        border-radius: 10px;
        margin-top: 10px;
    }
    .download-btn {
        background: linear-gradient(45deg, #1E90FF, #4169E1);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        margin: 5px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit App Configuration
st.set_page_config(page_title="Yasir YouTube Viral Tool", layout="wide", page_icon="🎬")

# Header with your name
st.markdown('<h1 class="main-header">Yasir YouTube Viral Finder</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Discover trending videos with precise filters</p>', unsafe_allow_html=True)

# Initialize session state for results
if 'results_df' not in st.session_state:
    st.session_state.results_df = None

# Sidebar for Filters
with st.sidebar:
    st.markdown("### 🔍 Custom Search Options")
    
    # A to Z Categories
    all_categories = {
        "All Categories": ["trending", "viral", "popular"],
        "Entertainment": ["comedy", "entertainment", "funny videos", "viral videos", "memes"],
        "Music": ["music", "songs", "music videos", "rap", "hip hop", "pop music"],
        "Gaming": ["gaming", "gameplay", "walkthrough", "esports", "pubg", "free fire"],
        "Education": ["education", "learning", "tutorial", "how to", "tips", "knowledge"],
        "Technology": ["technology", "tech", "gadgets", "review", "unboxing"],
        "Sports": ["sports", "cricket", "football", "highlights", "fitness"],
        "News": ["news", "current affairs", "breaking news", "politics"],
        "Cooking": ["cooking", "recipes", "food", "food vlog", "baking"],
        "Travel": ["travel", "travel vlog", "adventure", "tourism", "explore"],
        "Fashion": ["fashion", "style", "outfits", "makeup", "beauty"],
        "Health": ["health", "fitness", "workout", "yoga", "meditation"],
        "Business": ["business", "entrepreneur", "startup", "investing", "money"],
        "Motivation": ["motivation", "inspiration", "success", "self improvement"],
        "Religious": ["islamic", "religious", "quran", "hadith", "islam"],
        "Horror": ["horror", "scary", "ghost", "paranormal", "true horror"],
        "Drama": ["drama", "emotional", "relationship", "story", "short film"],
        "Animation": ["animation", "cartoon", "anime", "3d animation"],
        "Art": ["art", "drawing", "painting", "creative", "design"],
        "Science": ["science", "experiment", "discovery", "physics", "biology"],
        "History": ["history", "historical", "documentary", "ancient"],
        "Nature": ["nature", "wildlife", "animals", "environment"],
        "Kids": ["kids", "children", "toys", "family friendly"],
        "Other": ["other", "miscellaneous", "random"]
    }
    
    # Category Selection
    selected_category = st.selectbox("Select Main Category", list(all_categories.keys()))
    
    # Show keywords for selected category
    if selected_category != "Other":
        keywords = all_categories[selected_category]
        st.write(f"**Keywords:** {', '.join(keywords[:3])}...")
    
    # Custom Search Option
    st.markdown("---")
    st.markdown("### 🔎 Custom Search")
    custom_search = st.text_input("Enter ANY Other Keyword", "",
        help="Agar aap ki category yahan nahi hai, toh koi bhi keyword yahan likhein")
    
    # Date Range
    st.markdown("### 📅 Upload Date")
    days = st.number_input("Last How Many Days?", 1, 365, 30,
        help="Aaj se kitne din pichle tak ke videos dekhein")
    
    # Subscriber Range (Fully Customizable)
    st.markdown("---")
    st.markdown("### 👥 Subscriber Range")
    min_subs = st.number_input("Minimum Subscribers", 1, 10000000, 1,
        help="Kitne kam subscribers hon? 1 ya koi bhi value")
    max_subs = st.number_input("Maximum Subscribers", 1, 10000000, 1000000,
        help="Kitne zyada subscribers hon? 1000000 ya koi bhi value")
    
    # Views Range (Fully Customizable)
    st.markdown("### 👀 Views Range")
    min_views = st.number_input("Minimum Views", 1, 100000000, 1,
        help="Kitne kam views hon? 1 ya koi bhi value")
    max_views = st.number_input("Maximum Views", 1, 100000000, 10000000,
        help="Kitne zyada views hon? 10000000 ya koi bhi value")

# Main Search Interface
st.markdown("### 🎯 Search Settings")
num_results = st.slider("Number of Results per Keyword", 5, 50, 15,
    help="Har keyword ke liye kitne results chahiye? (15 recommended)")

# Use custom search or selected category
if custom_search:
    keywords = [custom_search]
    st.markdown(f'<div class="success-message">Custom Search: {custom_search}</div>', unsafe_allow_html=True)
else:
    keywords = all_categories[selected_category]
    st.markdown(f'<div class="success-message">Searching in: {selected_category}</div>', unsafe_allow_html=True)

if st.button("🚀 Find Viral Videos", use_container_width=True):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        all_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, keyword in enumerate(keywords):
            status_text.text(f"🔍 Searching: {keyword}...")
            
            # Search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": num_results,
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids:
                continue

            # Get video statistics
            stats_params = {"part": "statistics,contentDetails", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            # Get channel statistics
            if channel_ids:
                channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
                channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
                channel_data = channel_response.json()
            else:
                channel_data = {"items": []}

            if "items" not in stats_data:
                continue

            # Process results
            for j, (video, stat) in enumerate(zip(videos, stats_data["items"])):
                try:
                    # Get channel data if available
                    channel_info = channel_data["items"][j] if j < len(channel_data.get("items", [])) else {}
                    
                    views = int(stat["statistics"].get("viewCount", 0))
                    subs = int(channel_info.get("statistics", {}).get("subscriberCount", 0)) if channel_info else 0
                    
                    # Apply custom filters
                    if ((min_subs <= subs <= max_subs) and 
                        (min_views <= views <= max_views)):
                        
                        # Get thumbnail
                        thumbnails = video["snippet"].get("thumbnails", {})
                        thumbnail_url = thumbnails.get("high", {}).get("url") or thumbnails.get("medium", {}).get("url") or thumbnails.get("default", {}).get("url")
                        
                        # Format published date
                        published_at = video["snippet"].get("publishedAt", "")
                        if published_at:
                            pub_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                            formatted_date = pub_date.strftime("%Y-%m-%d %I:%M %p")
                        else:
                            formatted_date = "N/A"
                        
                        all_results.append({
                            "Title": video["snippet"].get("title", "N/A"),
                            "Description": video["snippet"].get("description", "")[:200],
                            "URL": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                            "Views": views,
                            "Subscribers": subs,
                            "Channel": video["snippet"].get("channelTitle", "N/A"),
                            "Keyword": keyword,
                            "Thumbnail": thumbnail_url,
                            "Published": formatted_date,
                            "Video_ID": video['id']['videoId']
                        })
                except Exception as e:
                    continue
            
            progress_bar.progress((i + 1) / len(keywords))

        # Store results in session state
        if all_results:
            st.session_state.results_df = pd.DataFrame(all_results)
        else:
            st.session_state.results_df = None

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("🔄 Please try again with different filters or try again later")

# Display results from session state
if st.session_state.results_df is not None:
    df = st.session_state.results_df
    
    # Download options
    st.markdown("### 💾 Download Options")
    col1, col2, col3 = st.columns(3)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "youtube_videos.csv", "text/csv")
    with col2:
        titles = "\n".join(df["Title"].tolist())
        st.download_button("📝 Download Titles", titles, "video_titles.txt", "text/plain")
    with col3:
        # Download all thumbnails option
        thumbnail_html = ""
        for _, row in df.iterrows():
            if row['Thumbnail']:
                thumbnail_html += f'<a href="{row["Thumbnail"]}" download="thumbnail_{row["Video_ID"]}.jpg">Thumbnail {row["Video_ID"]}</a><br>'
        
        if thumbnail_html:
            st.download_button("🖼️ Download Thumbnails List", thumbnail_html, "thumbnails.html", "text/html")

    # Show results with beautiful cards and tabs
    st.markdown(f"### 🎉 Found {len(df)} Viral Videos!")
    
    for _, row in df.iterrows():
        # Create tabs for each video
        tab1, tab2, tab3 = st.tabs(["📺 Video Info", "📝 Description", "🖼️ Thumbnail"])
        
        with tab1:
            st.markdown(f"""
            <div class="video-card">
                <h3>{row['Title']}</h3>
                <p><strong>📺 Channel:</strong> {row['Channel']}</p>
                <p><strong>👥 Subscribers:</strong> {row['Subscribers']:,}</p>
                <p><strong>👀 Views:</strong> {row['Views']:,}</p>
                <p><strong>🔍 Keyword:</strong> {row['Keyword']}</p>
                <p><strong>📅 Published:</strong> {row['Published']}</p>
                <p><a href="{row['URL']}" target="_blank" style="color: white; text-decoration: none;">
                   🎥 Watch Video</a></p>
            </div>
            """, unsafe_allow_html=True)
            
        with tab2:
            st.markdown("### Description")
            st.write(row['Description'])
            
            # Download description button
            st.download_button("📥 Download Description", row['Description'], f"description_{row['Video_ID']}.txt", "text/plain")
        
        with tab3:
            if row['Thumbnail']:
                st.image(row['Thumbnail'], caption="Video Thumbnail", use_column_width=True)
                # Download thumbnail button
                st.download_button("📥 Download Thumbnail", 
                                  requests.get(row['Thumbnail']).content, 
                                  f"thumbnail_{row['Video_ID']}.jpg", 
                                  "image/jpeg")
            else:
                st.write("No thumbnail available")

elif st.session_state.results_df is None:
    st.warning("""
    ### ❌ No videos found with your filters!
    
    **Try these solutions:**
    - 📈 Increase Maximum Subscribers/Views values
    - 📅 Increase Days to search (try 30+ days)
    - 🔍 Try different keywords
    - ❌ Remove some filters (specially subscriber filter)
    - 🎯 Try 'All Categories' first
    """)

# Footer with tips
st.markdown("---")
st.markdown("### 💡 Pro Tips:")
st.write("""
- **Start with broad filters** first, then refine
- **For small channels:** Subscribers 1-10,000
- **For medium channels:** Subscribers 10,000-100,000  
- **For viral potential:** Views/Subscribers ratio > 10
- **Try 'All Categories'** to discover new opportunities
- **Use tabs** to view detailed information about each video
- **Download thumbnails** for your favorite videos
""")
