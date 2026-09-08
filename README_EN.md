# chat-log-analysis

A WorkBuddy Skill that analyzes chat logs (QQ / WeChat / other IM exports) and generates data-driven analysis reports, plus interactive HTML gift pages for birthdays, anniversaries, and confessions.

## Features

- **Chat Log Parsing**: Supports JSONL / JSON / CSV formats exported by tools like QQChatExporter
- **Data Analysis**: Message volume, content type breakdown, monthly trends, 24-hour activity, session initiation, reply speed, topic preferences, nickname evolution
- **Markdown Report**: Structured report with raw data, reasoned judgments, and conclusions
- **Interactive HTML Gift Page**:
  - 7 Chart.js interactive charts, each with a data-backed conclusion
  - Relationship stage timeline + record highlights
  - Full-screen scrolling photo story timeline (polaroid style + timeline + emoji stickers)
  - Birthday cake interaction (click to blow candle → confetti → typewriter blessing)
  - Cursor-following hearts, click-to-zoom photos, BGM player
  - Scroll-triggered fade-in animations

## Installation

Copy this folder into your WorkBuddy user-level skills directory:

Windows:   C:\Users<username>.workbuddy\skills\chat-log-analysis
macOS/Linux: ~/.workbuddy/skills/chat-log-analysis/


Restart WorkBuddy or start a new conversation to activate.

## Usage

Tell your agent something like:

> "Analyze this QQ chat log and make an HTML birthday gift page"

The agent will automatically match this skill and follow the workflow:

1. Inspect and clean the raw data
2. Run `scripts/analyze.py` to produce `stats.json`
3. Generate a Markdown analysis report
4. Guide you to send photos one by one with the story behind each
5. Configure interactive elements (BGM, cake blessing, emoji stickers)
6. Generate the complete HTML page

## Dependencies

- Python 3.8+
- jieba (for Chinese word segmentation): `pip install jieba`
- Internet connection (template uses Chart.js CDN and Google Fonts)

## Project Structure

chat-log-analysis/
├── SKILL.md                          # Main skill document (workflow guide)
├── README.md                         # This file
├── .gitignore
├── references/
│   ├── pitfalls.md                   # Data analysis pitfalls & lessons
│   └── html_pitfalls.md              # HTML generation pitfalls & layout lessons
├── scripts/
│   ├── analyze.py                    # Chat log analysis script (outputs stats.json)
│   └── build_html.py                 # HTML builder (data + config → full HTML)
└── templates/
└── report_template.html          # HTML template with all interactions


## Chat Log Export Tools

- **QQ**: [QQChatExporter](https://github.com/shuakami/qq-chat-exporter) (exports JSONL)
- **WeChat**: Various third-party export tools

## Privacy

Chat logs are processed locally and the HTML page is delivered locally — nothing is uploaded to any server. Note that data does pass through the AI platform during the agent conversation, so evaluate sensitivity accordingly.

## License

MIT
