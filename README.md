# Handyman AI Assistant

Conversational AI assistant for a handyman business, built with LangChain and Google Gemini. The agent talks to a customer in natural language and can:

1. **Quote a job** — reads a Google Sheets pricing table and uses Gemini to estimate price, urgency, and complexity.
2. **Find availability** — queries Google Calendar for free slots on a given day/time window.
3. **Book the appointment** — creates a Google Calendar event after the customer confirms a slot.

## Architecture

| File | Role |
|---|---|
| [main.py](main.py) | Entry point. Builds the LangChain agent (`gemini-2.5-flash`), wires the three tools, runs an interactive terminal chat. |
| [mypricing_tool.py](mypricing_tool.py) | `pricing_tool` — reads `PricingSheet` from Google Sheets, asks Gemini to pick the best matching service and produce a JSON quote. |
| [myscheduling_tool.py](myscheduling_tool.py) | `scheduling_tool` — uses Google Calendar `freebusy.query` to compute open slots on the next requested weekday within a morning/afternoon/evening window. |
| [mycalendar_booking_tool.py](mycalendar_booking_tool.py) | `create_calendar_event_tool` — creates the calendar event after explicit user confirmation. |
| [read_sheets.py](read_sheets.py), [read_calendar.py](read_calendar.py), [check_models.py](check_models.py) | Standalone helper scripts used while developing/debugging. |

Timezone is hardcoded to `America/Chicago`.

## Prerequisites

- Python 3.11+
- A Google Cloud project with the **Sheets API** and **Calendar API** enabled
- A Google **service account** key (for reading the pricing sheet)
- An OAuth **desktop client** credentials file (for reading/writing the user's Google Calendar)
- One LLM API key — either **Google Gemini** or **Anthropic Claude** (the project is provider-agnostic)

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd handyman
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root. Pick **one** LLM provider:

```
# Default — use Google Gemini
LLM_PROVIDER=google
GOOGLE_API_KEY=your_gemini_api_key_here

# Or — use Anthropic Claude
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Optional model overrides:

```
GOOGLE_MODEL=gemini-2.5-flash                    # default
ANTHROPIC_MODEL=claude-haiku-4-5-20251001        # default
```

If `LLM_PROVIDER` is omitted, the project defaults to `google`.

### 3. Google Sheets — pricing data

1. Create a Google Sheet with a tab named `PricingSheet` and headers in row 1 (e.g. `service_type`, `base_price`, `urgency_multiplier`, `complexity_multiplier`, ...).
2. Create a service account in Google Cloud Console, download its JSON key, and save it in the project root as `service_account.json`.
3. Share the sheet with the service account's email (Viewer access is enough).
4. Copy the spreadsheet ID from its URL and update `SPREADSHEET_ID` in [mypricing_tool.py:9](mypricing_tool.py#L9).

### 4. Google Calendar — OAuth

1. In Google Cloud Console, create OAuth credentials of type **Desktop app**.
2. Download the JSON and save it in the project root as `credentials.json`.
3. The first time you run the app, a browser window will open for you to authorize calendar access. The resulting token is cached in `token.pickle` for future runs.

### 5. File layout after setup

```
handyman/
├── .env                    # GOOGLE_API_KEY
├── credentials.json        # OAuth desktop client (Calendar)
├── service_account.json    # Service account key (Sheets)
├── token.pickle            # Auto-generated after first OAuth login
├── main.py
├── mypricing_tool.py
├── myscheduling_tool.py
├── mycalendar_booking_tool.py
└── requirements.txt
```

All of `.env`, `credentials.json`, `service_account.json`, and `token.pickle` are gitignored — never commit them.

## Running

```bash
python main.py
```

Sample session:

```
User >> How much would it cost to install a ceiling fan?
... (agent calls pricing_tool, returns a quote)

User >> Do you have any morning slots on Friday?
... (agent calls scheduling_tool, lists numbered options)

User >> Option 2 works for me. Name is John Smith.
... (agent calls create_calendar_event_tool, confirms booking)

User >> exit
```

Type `quit`, `exit`, or `bye` to leave.

## Connecting to a new git remote

This project is set up as a fresh local git repo. To push it to a new remote:

```bash
git remote add origin <new-repo-url>
git add .
git commit -m "initial commit"
git branch -M main
git push -u origin main
```

## Troubleshooting

- **`FileNotFoundError: credentials.json` / `service_account.json`** — see Setup steps 3 and 4.
- **OAuth consent screen blocks login** — add your Google account as a test user in the OAuth consent screen settings.
- **Wrong timezone in slots** — change `TIMEZONE` in [myscheduling_tool.py:19](myscheduling_tool.py#L19) and [mycalendar_booking_tool.py:16](mycalendar_booking_tool.py#L16).
- **Re-authorize calendar** — delete `token.pickle` and run again.
