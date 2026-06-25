"""
Telegram Bot — the user interface for Content Intelligence OS.
All commands from the PRD are implemented here.
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from app.collectors.youtube_collector import collect_all_channels
from app.collectors.reddit_collector import collect_trending_topics
from app.collectors.trends_collector import get_trending_topics
from app.engines.intelligence_engine import (
    generate_daily_briefing,
    generate_script,
    score_idea,
    research_topic,
)
from app.storage.sheets import save_report, save_script

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", "0"))


def auth_required(func):
    """Restrict bot access to allowed Telegram user only."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ALLOWED_USER_ID:
            await update.message.reply_text("Access denied.")
            return
        await func(update, context)
    return wrapper


@auth_required
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 *Content Intelligence OS*\n\n"
        "AI-powered strategic content intelligence platform.\n\n"
        "Type /help to see all commands.",
        parse_mode="Markdown",
    )


@auth_required
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
*Available commands:*

*Trends:*
/trends — top trends (24h)
/trends7 — trends (7 days)
/forecast — future trends forecast

*Content:*
/ideas — top-10 content ideas
/ideas\_authority — ideas for authority building
/ideas\_clients — ideas for client attraction
/ideas\_viral — ideas for maximum views
/ideas\_english — ideas for English channel

*Analytics:*
/viral\_patterns — patterns of viral videos
/titles — best title patterns
/thumbnails — best thumbnail patterns

*Research:*
/research [topic] — deep topic research
/cross [topic] — cross-industry patterns

*Scripts:*
/script [topic] — full video script
/hook [topic] — 20 hook variants
/titles\_gen [topic] — 30 title variants
/score [idea] — score an idea (8 metrics)

*Personal brand:*
/authority — how to strengthen authority
/consulting — topics for client attraction
/next\_video — next recommended video
/content\_plan — content plan for the week

*System:*
/briefing — generate daily briefing now
/settings — system settings
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


@auth_required
async def cmd_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Collecting data and generating briefing... (~60 seconds)")

    try:
        youtube_data = collect_all_channels(max_results=5)
        reddit_data = collect_trending_topics(limit=5)
        trends_data = get_trending_topics()

        briefing = generate_daily_briefing(youtube_data, reddit_data, trends_data)
        save_report(briefing, "daily")

        for chunk in _split_message(briefing):
            await update.message.reply_text(chunk, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Briefing error: {e}")
        await update.message.reply_text(f"Error generating briefing: {e}")


@auth_required
async def cmd_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text("Usage: /script [topic]\nExample: /script unit economics for entrepreneurs")
        return

    await update.message.reply_text(f"✍️ Generating full script for: *{topic}*...", parse_mode="Markdown")

    try:
        script = generate_script(topic)
        save_script(topic, script)

        for chunk in _split_message(script):
            await update.message.reply_text(chunk, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Script error: {e}")
        await update.message.reply_text(f"Error generating script: {e}")


@auth_required
async def cmd_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idea = " ".join(context.args)
    if not idea:
        await update.message.reply_text("Usage: /score [idea]\nExample: /score Why 90% of entrepreneurs never escape operational mode")
        return

    await update.message.reply_text(f"📊 Scoring idea: *{idea}*...", parse_mode="Markdown")

    try:
        result = score_idea(idea)
        for chunk in _split_message(result):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


@auth_required
async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text("Usage: /research [topic]\nExample: /research unit economics")
        return

    await update.message.reply_text(f"🔬 Researching: *{topic}*...", parse_mode="Markdown")

    try:
        result = research_topic(topic)
        for chunk in _split_message(result):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


@auth_required
async def cmd_trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Fetching trends...")
    try:
        trends = get_trending_topics()
        text = "*TOP TRENDS (7 days):*\n\n"
        for i, t in enumerate(trends[:15], 1):
            text += f"{i}. {t['keyword']} — interest: {t['interest']}\n"
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


@auth_required
async def cmd_next_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎯 Calculating your next best video...")
    from app.engines.intelligence_engine import get_claude_client
    from config.prompts import MASTER_SYSTEM_PROMPT

    client = get_claude_client()
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
    try:
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=2048,
            system=MASTER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        result = message.content[0].text
        for chunk in _split_message(result):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


def _split_message(text: str, max_length: int = 4000) -> list[str]:
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    return chunks


def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("briefing", cmd_briefing))
    app.add_handler(CommandHandler("script", cmd_script))
    app.add_handler(CommandHandler("score", cmd_score))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("trends", cmd_trends))
    app.add_handler(CommandHandler("trends7", cmd_trends))
    app.add_handler(CommandHandler("next_video", cmd_next_video))

    logger.info("Content Intelligence OS bot started.")
    app.run_polling()
