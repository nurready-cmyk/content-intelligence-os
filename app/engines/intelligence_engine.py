"""
Intelligence Engine — sends collected data to Claude for analysis.
Returns structured insights for the daily briefing.
"""

import os
import anthropic
from config.prompts import MASTER_SYSTEM_PROMPT, DAILY_BRIEFING_PROMPT, SCRIPT_GENERATOR_PROMPT, IDEA_SCORING_PROMPT


def get_claude_client():
    return anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))


def generate_daily_briefing(youtube_data: list, reddit_data: list, trends_data: list) -> str:
    client = get_claude_client()

    context = _build_data_context(youtube_data, reddit_data, trends_data)

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        system=MASTER_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{DAILY_BRIEFING_PROMPT}\n\n--- COLLECTED DATA ---\n{context}",
            }
        ],
    )

    return message.content[0].text


def generate_script(topic: str) -> str:
    client = get_claude_client()

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        system=MASTER_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": SCRIPT_GENERATOR_PROMPT.format(topic=topic),
            }
        ],
    )

    return message.content[0].text


def score_idea(idea: str) -> str:
    client = get_claude_client()

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system=MASTER_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": IDEA_SCORING_PROMPT.format(idea=idea),
            }
        ],
    )

    return message.content[0].text


def research_topic(topic: str) -> str:
    client = get_claude_client()

    prompt = f"""
    Conduct a deep research on the topic: "{topic}"

    Include:
    1. Core patterns and laws behind this topic
    2. Counterintuitive insights most people miss
    3. Best company cases and historical examples
    4. Key statistics and research findings
    5. Cross-industry parallels
    6. Content angles with highest authority potential
    7. Top 5 video ideas on this topic with scores

    Quality standard: McKinsey / HBS level.
    Language: Russian.
    """

    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        system=MASTER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def _build_data_context(youtube_data: list, reddit_data: list, trends_data: list) -> str:
    parts = []

    if youtube_data:
        parts.append("YOUTUBE TOP VIDEOS (last 48h):")
        for v in youtube_data[:15]:
            parts.append(
                f"- [{v['view_count']:,} views] {v['title']} — {v['channel_title']}\n  {v['url']}"
            )

    if trends_data:
        parts.append("\nGOOGLE TRENDS (rising topics):")
        for t in trends_data[:10]:
            parts.append(f"- {t['keyword']}: interest={t['interest']} ({t['geo']})")

    if reddit_data:
        parts.append("\nREDDIT TRENDING:")
        for r in reddit_data[:10]:
            parts.append(f"- [{r['score']} upvotes] {r['title']} (r/{r['subreddit']})")

    return "\n".join(parts)
