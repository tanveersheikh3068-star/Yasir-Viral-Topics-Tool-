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
st.set_page_config(page_title="Yasir YouTube Viral Tool", layout="wide")
st.title("🎬 Yasir YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=7)

# List of broader keywords
keywords = [
    "True Horror Stories", "Scary Stories to Tell in the Dark", "Real Life Horror Stories",
    "Creepy Horror Stories", "Ghost Stories", "True Scary Stories", "Haunted House Stories",
    "Paranormal Activity Stories", "Sleep Paralysis Horror Stories", "Scary Story Animated",
    "Short Horror Film", "Reddit Horror Stories", "Two Sentence Horror Stories", "Dark Web Horror Stories",
    "Scary Camping Stories", "Haunted Places Horror", "Creepy Pasta Horror Stories",
    "Urban Legend Horror Stories", "True Crime Horror Stories", "Scary Bedtime Stories",
    "Real Ghost Stories", "Nightmare Horror Stories", "Creepy True Stories",
    "Scary Experience Stories", "Paranormal Horror Stories"
]

# Custom keyword option
st.markdown("### 🔍 Custom Keyword Search")
custom_keyword = st.text_input("Enter your own keyword (optional):", "")

# Replace keywords if custom keyword is provided
if custom_keyword:
    keywords = [custom_keyword]

# Fetch Data Button
if st.button("🚀 Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Iterate over the list of keywords
        for keyword in keywords:
            st.write(f"**Searching:** {keyword}")

            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 10,
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            # Check if "items" key exists
            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing video/channel data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"Failed to fetch video statistics for keyword: {keyword}")
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"Failed to fetch channel statistics for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Collect results
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_id = video["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))
                
                # Get thumbnail URL (high quality if available)
                thumbnails = video["snippet"].get("thumbnails", {})
                thumbnail_url = ""
                if "high" in thumbnails:
                    thumbnail_url = thumbnails["high"]["url"]
                elif "medium" in thumbnails:
                    thumbnail_url = thumbnails["medium"]["url"]
                elif "default" in thumbnails:
                    thumbnail_url = thumbnails["default"]["url"]

                # Only include channels with fewer than 50,000 subscribers
                if subs < 50000:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Video ID": video_id,
                        "Views": views,
                        "Subscribers": subs,
                        "Channel": video["snippet"].get("channelTitle", "N/A"),
                        "Thumbnail": thumbnail_url,
                        "Keyword": keyword
                    })

        # Display results
        if all_results:
            st.success(f"**Found {len(all_results)} results across all keywords!**")
            
            # Create DataFrame for download
            df = pd.DataFrame(all_results)
            
            # Download buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="youtube_viral_videos.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Download Titles only
                titles = "\n".join([f"{i+1}. {row['Title']}" for i, row in enumerate(all_results)])
                st.download_button(
                    label="📝 Download Titles",
                    data=titles,
                    file_name="video_titles.txt",
                    mime="text/plain"
                )
            
            with col3:
                # Thumbnail download guide
                st.info("🖼️ To download thumbnails, replace 'VIDEO_ID' in this URL: https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg")

            # Display results with thumbnails
            for result in all_results:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if result["Thumbnail"]:
                        st.image(result["Thumbnail"], use_column_width=True)
                    else:
                        st.write("No thumbnail available")
                
                with col2:
                    st.markdown(f"### {result['Title']}")
                    st.markdown(f"**Channel:** {result['Channel']}")
                    st.markdown(f"**Subscribers:** {result['Subscribers']:,}")
                    st.markdown(f"**Views:** {result['Views']:,}")
                    st.markdown(f"**Keyword:** {result['Keyword']}")
                    
                    # Video link that works
                    st.markdown(f"[🎥 Watch Video on YouTube]({result['URL']})")
                    
                    st.markdown(f"**Description:** {result['Description']}...")
                
                st.markdown("---")
                
        else:
            st.warning("No results found for channels with fewer than 50,000 subscribers. Try increasing the subscriber limit or search days.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please check your internet connection and try again.")

# Add instructions
st.markdown("---")
st.markdown("### 💡 Instructions:")
st.write("""
1. Enter number of days to search (1-30)
2. Use custom keyword or default horror keywords
3. Click 'Fetch Data' to find viral videos
4. Download results as CSV or text
5. Use YouTube links to watch videos
""")
