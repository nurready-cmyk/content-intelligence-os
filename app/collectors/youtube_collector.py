"""
YouTube Data API collector.
Fetches recent videos, stats, and comments from monitored channels.
"""

import os
from googleapiclient.discovery import build
from config.channels import YOUTUBE_CHANNELS


def get_youtube_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    return build("youtube", "v3", developerKey=api_key)


def get_recent_videos(channel_id: str, max_results: int = 10) -> list[dict]:
    youtube = get_youtube_client()

    search_response = youtube.search().list(
        channelId=channel_id,
        part="snippet",
        order="date",
        maxResults=max_results,
        type="video",
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
    if not video_ids:
        return []

    videos_response = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids),
    ).execute()

    videos = []
    for item in videos_response.get("items", []):
        stats = item.get("statistics", {})
        videos.append({
            "id": item["id"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"][:500],
            "published_at": item["snippet"]["publishedAt"],
            "channel_title": item["snippet"]["channelTitle"],
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "thumbnail": item["snippet"]["thumbnails"].get("high", {}).get("url", ""),
            "url": f"https://youtube.com/watch?v={item['id']}",
        })

    return sorted(videos, key=lambda x: x["view_count"], reverse=True)


def get_top_comments(video_id: str, max_results: int = 50) -> list[dict]:
    youtube = get_youtube_client()

    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            order="relevance",
            maxResults=max_results,
        ).execute()
    except Exception:
        return []

    comments = []
    for item in response.get("items", []):
        top = item["snippet"]["topLevelComment"]["snippet"]
        comments.append({
            "text": top["textDisplay"],
            "like_count": top["likeCount"],
            "author": top["authorDisplayName"],
        })

    return comments


def collect_all_channels(max_results: int = 5) -> list[dict]:
    # YouTube API temporarily disabled — returns empty list until API key is fixed
    return []
