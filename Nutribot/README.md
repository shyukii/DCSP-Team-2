# Nutribot

Telegram bot for composting and gardening assistance.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with required variables from `.env.example`.

## Run with webhook (production)

1. Start ngrok:
```bash
ngrok http 8000
```

2. Update `WEBHOOK_URL` in `.env` with ngrok URL

3. Run with gunicorn:
```bash
gunicorn app:app -b 0.0.0.0:8000
```

## Run with polling (development)

Remove `WEBHOOK_URL` from `.env` and run:
```bash
python main.py
```