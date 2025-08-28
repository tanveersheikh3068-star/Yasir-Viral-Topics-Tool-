import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

# YouTube API Key
API_KEY = "AIzaSyBpvV27UugXepVM_MrXtKtqr3rza9h0s7w"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Configuration
st.set_page_config(page_title="Ultimate YouTube Viral Finder", layout="wide")
st.title("🎬 Ultimate YouTube Viral Topics Tool")

# Sidebar for Filters
with st.sidebar:
    st.header("🔍 Custom Search Options")
    
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
        st.write(f"**Keywords in {selected_category}:**")
        st.write(", ".join(keywords))
    else:
        st.info("Select 'Custom Search' below for other topics")
    
    # Custom Search Option
    st.subheader("🔎 Custom Search")
    custom_search = st.text_input("Enter ANY Other Keyword (Optional)", "",
        help="Agar aap ki category yahan nahi hai, toh koi bhi keyword yahan likhein")
    
    # Subscriber Range (Fully Customizable)
    st.subheader("👥 Subscriber Range")
    min_subs = st.number_input("Minimum Subscribers", 0, 100000000, 0,
        help="Kitne kam subscribers hon? 0 ya koi bhi value")
    max_subs = st.number_input("Maximum Subscribers", 0, 100000000, 1000000,
        help="Kitne zyada subscribers hon? 1000000 ya koi bhi value")
    
    # Views Range (Fully Customizable)
    st.subheader("👀 Views Range")
    min_views = st.number_input("Minimum Views", 0, 1000000000, 1000,
        help="Kitne kam views hon? 1000 ya koi bhi value")
    max_views = st.number_input("Maximum Views", 0, 1000000000, 10000000,
        help="Kitne zyada views hon? 10000000 ya koi bhi value")
    
    # Date Range
    st.subheader("📅 Upload Date")
    days = st.slider("Last How Many Days?", 1, 365, 7,
        help="Aaj se kitne din pichle tak ke videos dekhein")

# Main Search Interface
st.subheader("🎯 Search Settings")
num_results = st.slider("Number of Results per Keyword", 5, 50, 10)

# Use custom search or selected category
if custom_search:
    keywords = [custom_search]
    st.success(f"Custom Search: {custom_search}")
else:
    keywords = all_categories[selected_category]
    st.success(f"Searching in: {selected_category}")

if st.button("🚀 Find Viral Videos", type="primary", use_container_width=True):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        all_results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, keyword in enumerate(keywords):
            status_text.text(f"🔍 Searching: {keyword}")
            
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
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

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
                        
                        all_results.append({
                            "Title": video["snippet"].get("title", "N/A"),
                            "Description": video["snippet"].get("description", "")[:200],
                            "URL": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
                            "Views": views,
                            "Subscribers": subs,
                            "Channel": video["snippet"].get("channelTitle", "N/A"),
                            "Keyword": keyword,
                            "Thumbnail": video["snippet"].get("thumbnails", {}).get("high", {}).get("url", "")
                        })
                except:
                    continue
            
            progress_bar.progress((i + 1) / len(keywords))

        # Display results
        if all_results:
            df = pd.DataFrame(all_results)
            
            # Download options
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = df.to_csv(index=False)
                st.download_button("📥 Download CSV", csv, "youtube_videos.csv", "text/csv")
            with col2:
                titles = "\n".join(df["Title"].tolist())
                st.download_button("📝 Download Titles", titles, "video_titles.txt", "text/plain")
            with col3:
                st.info("🖼️ Thumbnails available in CSV")

            # Show results
            st.subheader(f"🎉 Found {len(all_results)} Videos!")
            
            for _, row in df.iterrows():
                with st.expander(f"{row['Title']} ({row['Views']:,} views)"):
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if row["Thumbnail"]:
                            st.image(row["Thumbnail"], width=150)
                    
                    with col2:
                        st.write(f"**Channel:** {row['Channel']}")
                        st.write(f"**Subscribers:** {row['Subscribers']:,}")
                        st.write(f"**Views:** {row['Views']:,}")
                        st.write(f"**Keyword:** {row['Keyword']}")
                    
                    with col3:
                        st.markdown(f"[🎥 Watch Video]({row['URL']})")
                        st.write(f"**Score:** {row['Views']/max(1, row['Subscribers']):.1f}x")
                    
                    st.write(f"**Description:** {row['Description']}...")

        else:
            st.warning("""
            ❌ No videos found with your filters!
            
            **Try these solutions:**
            1. 📈 Increase Maximum Subscribers/Views values
            2. 📅 Increase Days to search
            3. 🔍 Try different keywords
            4. ❌ Remove some filters
            """)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("🔄 Please try again with different filters")

# Footer with tips
st.markdown("---")
st.subheader("💡 Pro Tips:")
st.write("""
- **Subscriber Range:** 0-5000 (Small channels), 0-100000 (Medium), 0-1000000 (Large)
- **Views Range:** 1000-100000 (Good engagement), 100000+ (Viral potential)
- **Custom Search:** Koi bhi topic search karne ke liye!
- **Score:** (Views/Subscribers) - Higher score = better engagement
""")
