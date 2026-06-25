"""
Scheduler — sends the daily briefing automatically at configured time.
Runs as a background process alongside the Telegram bot.
"""

import os
import asyncio
import logging
from datetime import datetime
import schedule
import time

from telegram import Bot

from app.collectors.youtube_collector import collect_all_channels
from app.collectors.reddit_collector import collect_trending_topics
from app.collectors.trends_collector import get_trending_topics
from app.engines.intelligence_engine import generate_daily_briefing
from app.storage.sheets import save_report

logger = logging.getLogger(__name__)


async def send_daily_briefing():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    user_id = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", "0"))

    if not token or not user_id:
        logger.error("Bot token or user ID not configured")
        return

    bot = Bot(token=token)

    try:
        await bot.send_message(chat_id=user_id, text="☀️ Good morning! Generating your Daily Intelligence Briefing...")

        youtube_data = collect_all_channels(max_results=5)
        reddit_data = collect_trending_topics(limit=5)
        trends_data = get_trending_topics()

        briefing = generate_daily_briefing(youtube_data, reddit_data, trends_data)
        save_report(briefing, "daily")

        max_len = 4000
        for i in range(0, len(briefing), max_len):
            chunk = briefing[i:i+max_len]
            await bot.send_message(chat_id=user_id, text=chunk, parse_mode="Markdown")

        logger.info(f"Daily briefing sent at {datetime.now()}")

    except Exception as e:
        logger.error(f"Failed to send daily briefing: {e}")
        try:
            await bot.send_message(chat_id=user_id, text=f"⚠️ Error generating briefing: {e}")
        except Exception:
            pass


def run_scheduler():
    report_time = os.getenv("DAILY_REPORT_TIME", "08:00")

    schedule.every().day.at(report_time).do(
        lambda: asyncio.run(send_daily_briefing())
    )

    logger.info(f"Scheduler started. Daily briefing at {report_time}")

    while True:
        schedule.run_pending()
        time.sleep(60)
