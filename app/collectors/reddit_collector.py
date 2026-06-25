"""
Reddit collector — finds trending discussions in business/entrepreneurship subreddits.
"""

import os
import praw


SUBREDDITS = [
    "Entrepreneur",
    "business",
    "smallbusiness",
    "startups",
    "marketing",
    "SEO",
    "personalfinance",
    "investing",
]


def get_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "ContentIntelligenceOS/1.0"),
    )


def get_hot_posts(subreddit_name: str, limit: int = 10) -> list[dict]:
    reddit = get_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)

    posts = []
    for post in subreddit.hot(limit=limit):
        posts.append({
            "title": post.title,
            "score": post.score,
            "upvote_ratio": post.upvote_ratio,
            "num_comments": post.num_comments,
            "url": post.url,
            "subreddit": subreddit_name,
            "selftext": post.selftext[:300] if post.selftext else "",
        })

    return posts


def collect_trending_topics(limit: int = 5) -> list[dict]:
    all_posts = []
    for sub in SUBREDDITS:
        try:
            posts = get_hot_posts(sub, limit=limit)
            all_posts.extend(posts)
        except Exception:
            continue

    return sorted(all_posts, key=lambda x: x["score"], reverse=True)
