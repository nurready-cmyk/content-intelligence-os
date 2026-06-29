"""
Intelligence Engine — sends collected data to Gemini for analysis.
Returns structured insights for the daily briefing.
"""

import os
from google import genai
from google.genai import types
from config.prompts import MASTER_SYSTEM_PROMPT, DAILY_BRIEFING_PROMPT, SCRIPT_GENERATOR_PROMPT, IDEA_SCORING_PROMPT


def _ask(prompt: str, max_tokens: int = 4096) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=MASTER_SYSTEM_PROMPT,
            max_output_tokens=max_tokens,
            temperature=0.7,
        ),
    )
    return response.text


def generate_daily_briefing(youtube_data: list, reddit_data: list, trends_data: list) -> str:
    context = _build_data_context(youtube_data, reddit_data, trends_data)
    if not context.strip():
        context = "No external data collected today. Use your own knowledge of current global business, entrepreneurship, AI, and personal development trends to generate the briefing."
    return _ask(f"{DAILY_BRIEFING_PROMPT}\n\n--- COLLECTED DATA ---\n{context}", max_tokens=4096)


def generate_script(topic: str) -> str:
    return _ask(SCRIPT_GENERATOR_PROMPT.format(topic=topic), max_tokens=8192)


def score_idea(idea: str) -> str:
    return _ask(IDEA_SCORING_PROMPT.format(idea=idea), max_tokens=1024)


def research_topic(topic: str) -> str:
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
    return _ask(prompt, max_tokens=4096)


def get_next_video() -> str:
    prompt = """
    Based on the content priority weights and the goal of building an international expert brand,
    recommend the SINGLE BEST video to shoot right now.

    Provide:
    1. Topic and title (3 variants)
    2. Why THIS topic RIGHT NOW (strategic reasoning)
    3. All 8 scores
    4. Hook (top-3)
    5. Key angle that makes it unique
    6. Estimated impact in 30/90/365 days

    Language: Russian.
    """
    return _ask(prompt, max_tokens=2048)


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
