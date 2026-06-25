"""
Content Intelligence OS — entry point.
Starts the Telegram bot and the daily scheduler in parallel threads.
"""

import threading
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from app.telegram.bot import run_bot
from app.scheduler.daily_scheduler import run_scheduler


def main():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    run_bot()


if __name__ == "__main__":
    main()
