import os
from dotenv import load_dotenv
from youtube_api import YouTubeAPI

load_dotenv()
yt_client_id = os.getenv("YOUTUBE_CLIENT_ID")
yt_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
yt_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

if not (yt_client_id and yt_client_secret and yt_refresh_token):
    print("Keys missing")
    exit(1)

try:
    yt_api = YouTubeAPI(yt_client_id, yt_client_secret, yt_refresh_token)
    stats = yt_api.get_channel_stats()
    print("Stats:", stats)
    
    # Get the user's channel ID
    request = yt_api.youtube.channels().list(part="contentDetails", mine=True)
    response = request.execute()
    
    if "items" in response and len(response["items"]) > 0:
        uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Get recent videos
        playlist_req = yt_api.youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=10
        )
        playlist_res = playlist_req.execute()
        
        video_ids = []
        for item in playlist_res.get("items", []):
            vid_id = item["snippet"]["resourceId"]["videoId"]
            video_ids.append(vid_id)
            
        if video_ids:
            # Get view counts for these videos
            videos_req = yt_api.youtube.videos().list(
                part="snippet,statistics",
                id=",".join(video_ids)
            )
            videos_res = videos_req.execute()
            print("\nRecent Videos:")
            for item in videos_res.get("items", []):
                title = item["snippet"]["title"]
                views = item["statistics"].get("viewCount", "0")
                likes = item["statistics"].get("likeCount", "0")
                print(f"Views: {views} | Likes: {likes} | Title: {title}")
except Exception as e:
    print(f"Error: {e}")
