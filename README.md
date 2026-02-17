# Career Pilot

Career Pilot is a local-first FastAPI app for collecting LinkedIn job posts, analyzing them with an LLM, and managing outreach from a dashboard.

This README explains exactly how to run it locally for development and day-to-day use.

## What It Does

- Searches LinkedIn post URLs using Serper, or ingests URLs from CSV.
- Fetches each post using Playwright with your logged-in LinkedIn browser session.
- Extracts structured lead data with Gemini or OpenAI.
- Stores leads and visited links in SQLite.
- Lets you review/update lead state and send emails via Gmail API.

## Tech Stack

- Python + FastAPI + Uvicorn
- SQLAlchemy + SQLite
- Playwright (Chromium)
- OpenAI and/or Gemini SDK
- Google API client (Gmail)
- Jinja2 + HTMX + Bootstrap UI

## Prerequisites

- Python 3.10+ (3.11/3.12 recommended)
- `pip`
- A LinkedIn account (for authenticated page fetches)
- At least one LLM API key:
  - Gemini (`GEMINI_API_KEY`) or
  - OpenAI (`OPENAI_API_KEY`)
- Serper API key (for automatic search mode)
- Optional: Gmail API token JSON for sending emails

## 1) Clone And Enter Project

```bash
git clone <your-repo-url>
cd career-pilot
```

## 2) Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## 3) Install Dependencies

```bash
pip install -r requirements.txt
pip install playwright
python -m playwright install chromium
```

Why Playwright is separate: the app imports `playwright.async_api`, but `playwright` is not currently listed in `requirements.txt`.

## 4) Configure Environment Variables

The app reads settings from process environment variables (`os.getenv`).
If you use a `.env` file, load it into your shell before starting the app.

### Required/Important Variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `LLM_PROVIDER` | Yes (practically) | `gemini` | Choose `gemini` or `openai`. |
| `GEMINI_API_KEY` | Required if `LLM_PROVIDER=gemini` | empty recommended | Gemini auth key. |
| `OPENAI_API_KEY` | Required if `LLM_PROVIDER=openai` | empty | OpenAI auth key. |
| `SERPER_API_KEY` | Required for Run Search in UI | empty recommended | Serper search API key. |
| `DATABASE_URL` | Optional | `sqlite:///./job_agent.db` | SQLite DB path/URL. |
| `GMAIL_TOKEN_FILE` | Optional | `gmail_token.json` | Gmail OAuth token path. |
| `OPENAI_MODEL` | Optional | `gpt-4o-mini` | OpenAI model name. |
| `GEMINI_MODEL` | Optional | `gemini-2.0-flash` | Gemini model name. |
| `LLM_MAX_RETRIES` | Optional | `5` | LLM retry count on rate limit. |
| `LLM_BACKOFF_BASE_SECONDS` | Optional | `1.0` | LLM exponential backoff base. |
| `MAX_SEARCH_RESULTS_CAP` | Optional | `100` | Upper cap for search result collection. |

### Example `.env` (safe template)

```env
DATABASE_URL=sqlite:///./job_agent.db

LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash

# If using OpenAI instead
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_openai_api_key
# OPENAI_MODEL=gpt-4o-mini

SERPER_API_KEY=your_serper_api_key
GMAIL_TOKEN_FILE=gmail_token.json

LLM_MAX_RETRIES=5
LLM_BACKOFF_BASE_SECONDS=1.0
MAX_SEARCH_RESULTS_CAP=100
```

Load `.env` into shell:

```bash
set -a
source .env
set +a
```

## 5) Required Local Files

### LinkedIn session state

`app/services/fetch_service.py` uses:

- `linkedin_session.json` as Playwright `storage_state`

So you must have a valid `linkedin_session.json` in repo root with active LinkedIn login cookies/session.
If invalid/expired, post fetching will fail.

Generate it with your helper script:

```bash
python save_linkedin_session.py
```

Note: some setups may use the filename `save_linked_session.py`; both names are ignored in `.gitignore`.

### Resume for outbound email (optional)

`app/services/mail_service.py` attaches `resume.pdf` if present in repo root.

### Gmail token (optional)

To use send-mail endpoints, provide a valid Gmail OAuth token JSON file (default name: `gmail_token.json`).

Generate it with your helper script:

```bash
python gmail_token.py
```

This should create/update `gmail_token.json` in project root.

## 5.1) Token/Session Script Setup (One-Time)

If you use local helper scripts to generate auth artifacts, keep them in repo root as:

- `gmail_token.py`
- `save_linkedin_session.py` (or `save_linked_session.py`)

Then run:

```bash
python gmail_token.py
python save_linkedin_session.py
```

Expected output artifacts:

- `gmail_token.json`
- `linkedin_session.json`

## 6) Run The App

```bash
uvicorn app.main:app --reload
```

Open:

- Dashboard: `http://127.0.0.1:8000/`
- Leads: `http://127.0.0.1:8000/leads`

## 7) Typical Local Workflow

1. Open `/`.
2. Use **Run Search** (keywords, days, max results) or **Upload CSV**.
3. App fetches + analyzes posts and stores accepted leads (`score >= 5`) as `IN_REVIEW`.
4. Open `/leads` to review/edit leads and move states.
5. When state moves `IN_REVIEW -> APPROVED`, draft email is generated.
6. Send individual or bulk email (if Gmail token is configured).

## CSV Input Format

- Plain CSV.
- First column must contain URL.
- Header row is optional.
- Rows where first value does not start with `http` are skipped.

Example:

```csv
https://www.linkedin.com/posts/example-post-1
https://www.linkedin.com/posts/example-post-2
```

## Run Tests

```bash
pip install -r requirements.txt
python -m pytest -q
```

## Logs And Database

- SQLite DB file (default): `job_agent.db`
- Logs: `logs/logs-DD-MM-YYYY/`
  - `run.log`
  - `llm_calls.log`
  - `errors.log`

## Important Notes

- On startup, `ensure_schema()` may drop and recreate tables if it detects legacy incompatible schema for `leads`. Back up your DB before upgrading.
- Mail sender address is currently hardcoded in `app/services/mail_service.py` (`YOUR_EMAIL`).
- `resume.pdf` filename/path is also hardcoded in `app/services/mail_service.py`.

## Troubleshooting

- `ValueError: GEMINI_API_KEY missing` or `OPENAI_API_KEY missing`:
  - Set the API key matching `LLM_PROVIDER`.
- Search returns zero links:
  - Verify `SERPER_API_KEY` and quota.
- Fetch errors from Playwright or LinkedIn:
  - Recreate/refresh `linkedin_session.json`.
  - Confirm Chromium is installed (`python -m playwright install chromium`).
- Gmail send fails with token error:
  - Replace `gmail_token.json` with a valid token containing refresh token.
- `pytest` command not found:
  - Use `python -m pytest -q` inside activated venv.
