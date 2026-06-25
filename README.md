# Content Intelligence OS
### AI-powered Strategic Content Intelligence Platform

> **Mission:** Build an international expert brand through intelligent content — systematically, without guesswork.

---

## What is this?

Content Intelligence OS is a Telegram bot powered by Claude AI that acts as your:
- Virtual analytics department
- Research center
- Content strategist
- Script writer
- Strategic advisor

It analyzes YouTube, Reddit, Google Trends, and other sources — then tells you exactly **what content to create and why.**

---

## Key Features

- **Daily Briefing** — sent every morning at 08:00 with top trends, content ideas, and one recommended video
- **Script Generator** — full video scripts with hooks, research, cases, laws
- **Idea Scoring** — rate any idea on 8 strategic metrics
- **Deep Research** — McKinsey/HBS-level analysis on any topic
- **All Telegram commands** from the PRD

---

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/nurready-cmyk/content-intelligence-os.git
cd content-intelligence-os
pip install -r requirements.txt
cp .env.example .env
```

### 2. Fill in `.env`

```env
CLAUDE_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ALLOWED_USER_ID=your_telegram_id
YOUTUBE_API_KEY=your_key
GOOGLE_SHEETS_ID=your_sheet_id
```

### 3. Add your YouTube channels

Edit `config/channels.py` — add the channel IDs you want to monitor.

### 4. Run

```bash
python main.py
```

Or with Docker:

```bash
docker-compose up -d
```

---

## Telegram Commands

| Command | Description |
|---|---|
| `/briefing` | Generate daily briefing now |
| `/script [topic]` | Full video script |
| `/score [idea]` | Score idea on 8 metrics |
| `/research [topic]` | Deep research |
| `/trends` | Top trending topics |
| `/next_video` | Best video to shoot right now |

---

## Tech Stack

| Component | Tool | Cost |
|---|---|---|
| AI Brain | Claude API (Anthropic) | Pay per use |
| YouTube data | YouTube Data API | Free |
| Trends | Google Trends | Free |
| Social signals | Reddit API | Free |
| Storage | Google Sheets | Free |
| Interface | Telegram Bot API | Free |
| Server | Hetzner VPS CX11 | ~$4/month |

---

## Roadmap

```
v1 → Telegram Bot + Google Sheets + Claude + YouTube + Daily Reports   ← YOU ARE HERE
v2 → PostgreSQL + Advanced Analytics + Comment Intelligence
v3 → Web Dashboard + Personal Learning Engine
v4 → Multi-Agent: Research / Strategy / Content / Audience
v5 → Personal Board of Advisors (McKinsey + Media Strategist + Psychologist...)
```

---

*Content Intelligence OS · v1.0 · 2025*
