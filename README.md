# Bizynex Telegram Sales Agent

A production Persian-language Telegram sales bot for **Bizynex**, built with Django 5 and aiogram 3. It introduces Bizynex's services, compares options, walks customers through a live project-cost estimator, collects structured project requests, and notifies the team admin — all in fluent Persian.

## Features

- 🏢 About Bizynex, 💼 services catalog (6 services), 🆚 WordPress-vs-custom comparison
- 💰 Per-service project estimator — a real pricing engine, never a fixed number
- 📝 Multi-step project request form with per-field editing and file attachments
- 📞 Contact info, ❓ FAQ, 📂 portfolio placeholder
- Admin notification on every submitted request, containing every field
- Structured logging, global error handling, HTML-injection-safe messages
- Runs entirely on Render's free tier (see [Free-tier notes](#free-tier-notes))

## Tech stack

Python 3.13 · Django 5 · aiogram 3 · PostgreSQL · Gunicorn + Uvicorn (ASGI) · pydantic-settings · structlog · Black · Ruff · Pytest

## Architecture

Clean Architecture, strictly layered:

```
core/
  domain/            Pure Python — entities, value objects, the estimator's
                      pricing engine, repository interfaces. No Django, no I/O.
  application/        Framework-free validation/use-case logic.
  infrastructure/      Django ORM repositories, the Telegram bot (FSM storage,
                      dispatcher, keep-alive task), structlog config.
apps/
  accounts/           Customer persistence.
  requests/            Estimation / ProjectRequest / ProjectAttachment persistence.
  bot/                 Presentation layer — aiogram handlers, keyboards, FSM
                      states, Persian content, the Django webhook view.
config/               Django settings (env-driven), ASGI entrypoint, URLs.
tests/                 Mirrors the structure above.
```

Business logic never lives in a handler — handlers only orchestrate: validate input, call into `core/`, render Persian content, and manage FSM state.

## Local development

### Prerequisites

- Python 3.13+
- A local PostgreSQL instance (or any reachable Postgres)
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
cp .env.example .env
```

Edit `.env` with your local Postgres URL and bot token (see [Environment variables](#environment-variables) below).

```bash
python manage.py migrate
python manage.py check
```

### Running the test suite

```bash
python -m pytest
```

Most of the suite (200+ tests) needs no database — pure domain logic and handler-level tests using in-memory FSM storage. A handful of tests are explicitly marked as needing a live Postgres connection (repository round-trips, FSM storage round-trips, one full webhook-dispatch test) and are skippable if you don't have one running locally:

```bash
python -m pytest --ignore=tests/infrastructure/test_fsm_storage_db.py \
  --ignore=tests/infrastructure/test_customer_repository_db.py \
  --ignore=tests/infrastructure/test_estimation_repository_db.py \
  --ignore=tests/infrastructure/test_project_request_repository_db.py \
  --ignore=tests/bot/test_customer_identity_middleware_db.py \
  -k "not test_valid_start_command_dispatches_end_to_end"
```

With coverage:

```bash
python -m pytest --cov=core --cov=apps --cov-report=term-missing
```

### Code quality

```bash
black .
ruff check . --fix
```

### Testing the bot locally

The bot runs on **webhooks**, which need a public HTTPS URL — there's no meaningful "run the bot locally against Telegram" workflow without a tunnel (ngrok or similar). For local iteration, rely on the test suite (it exercises full conversation flows without touching Telegram's API) and `python manage.py check`. Deploy to Render to test against the real Telegram app.

## Deployment (Render)

### Prerequisites

1. A [Render](https://render.com) account.
2. A Telegram bot token from [@BotFather](https://t.me/BotFather) (`/newbot`).
3. Your numeric Telegram user ID — message [@userinfobot](https://t.me/userinfobot) to get it. This is where project request notifications go (`ADMIN_ID`).
4. Push this repository to GitHub/GitLab — Render deploys from a git remote.

### Option A — Blueprint deploy (`render.yaml`)

1. In the Render dashboard: **New → Blueprint**, pick this repository.
2. Render reads `render.yaml` and provisions the web service and the free Postgres database together.
3. It will prompt you for the two secrets not stored in the blueprint: `BOT_TOKEN` and `ADMIN_ID`. Enter them.
4. Deploy. `SECRET_KEY` and `WEBHOOK_SECRET` are auto-generated; `DATABASE_URL` is wired automatically from the provisioned database.

If the Blueprint fails to parse (Render's schema does change over time), use Option B — it's the exact same setup done by hand.

### Option B — Manual dashboard setup

**1. Create the database**

Render dashboard → **New → PostgreSQL**. Name it (e.g. `bizynex-db`), free plan, same region you'll use for the web service. Once created, copy its **Internal Database URL**.

**2. Create the web service**

Render dashboard → **New → Web Service** → connect this repository.

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt && python manage.py migrate --noinput` |
| Start Command | `gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --workers 1 --timeout 60 --bind 0.0.0.0:$PORT` |
| Plan | Free |
| Health Check Path | `/health/` |

**3. Set environment variables**

In the web service's **Environment** tab:

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `False` |
| `SECRET_KEY` | a random 50+ char string — generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DATABASE_URL` | the Internal Database URL from step 1 |
| `BOT_TOKEN` | your token from BotFather |
| `ADMIN_ID` | your numeric Telegram user ID |
| `WEBHOOK_SECRET` | another random string (same command as above) |
| `WEBHOOK_PATH` | `/webhook/` |
| `KEEPALIVE_ENABLED` | `True` |
| `KEEPALIVE_INTERVAL_SECONDS` | `780` |
| `LOG_LEVEL` | `INFO` |

Do **not** set `RENDER_EXTERNAL_URL` — Render injects it automatically, and the app reads it to register the Telegram webhook and to extend `ALLOWED_HOSTS` at startup.

**4. Deploy**

Render builds and starts the service. On startup, the app automatically calls Telegram's `setWebhook` with your service's URL — no manual step needed.

### Verifying it worked

Open `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo` in a browser. You should see `"url"` pointing at your Render service's `/webhook/` path and no `last_error_message`. Then message your bot `/start` on Telegram.

### Free-tier notes

- **Free Postgres expires.** Render's free Postgres plan is a 30-day trial — it's suspended and eventually deleted unless upgraded to a paid instance (~$7/mo Starter). This is a Render billing decision, not something the app works around; budget for it if this goes to real customers.
- **Cold starts.** A free web service sleeps after ~15 minutes with no inbound HTTP traffic and takes 30–60s to wake on the next request. The app runs its own keep-alive self-ping (`core/infrastructure/telegram/keepalive.py`) every 13 minutes by default, which — because it's a real inbound request to the service's own `/health/` endpoint — keeps it from sleeping in normal operation. This uses ~720 of Render's 750 free monthly instance-hours; fine as long as this is the only free service on the account.
- **Single worker.** The start command runs one Uvicorn worker to fit the free plan's 512MB RAM — concurrency is handled by asyncio within that one process, which is sufficient for this bot's traffic profile.

## Environment variables

See [`.env.example`](.env.example) for the full list with inline explanations. Summary:

| Variable | Required | Notes |
|---|---|---|
| `ENVIRONMENT` | yes | `development` or `production` |
| `DEBUG` | yes | `True` locally, `False` in production |
| `SECRET_KEY` | yes | Django's cryptographic signing key |
| `ALLOWED_HOSTS` | no | defaults to `localhost,127.0.0.1`; production auto-adds the Render host |
| `DATABASE_URL` | yes | PostgreSQL connection string |
| `BOT_TOKEN` | yes | from BotFather |
| `ADMIN_ID` | yes | numeric Telegram user ID for request notifications |
| `WEBHOOK_SECRET` | yes | verifies incoming webhook calls are really from Telegram |
| `WEBHOOK_PATH` | no | defaults to `/webhook/` |
| `RENDER_EXTERNAL_URL` | no | injected by Render — never set manually |
| `KEEPALIVE_ENABLED` | no | defaults to `True` |
| `KEEPALIVE_INTERVAL_SECONDS` | no | defaults to `780` (13 min) |
| `LOG_LEVEL` | no | defaults to `INFO` |

## Extending the project

- **New service**: add it to `ServiceType` (`core/domain/value_objects/service_type.py`), its price range in `core/domain/catalog.py`, its catalog entry in `apps/bot/content/services.py`, and its estimator question set in `core/domain/estimator/config.py`. Everything else (menus, keyboards, page registry) picks it up automatically.
- **New static page**: add one entry to `apps/bot/pages/registry.py` — no handler changes needed.
- **Tuning estimator pricing**: every score and duration band lives in `core/domain/estimator/config.py`, isolated from the conversation-flow code in `apps/bot/handlers/estimator.py`.
