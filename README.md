# LingoPika

Telegram English learning platform (Mini App).

## Run backend locally
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload --port 8000
```

## Run frontend
```bash
cd frontend
npm install
npm run dev
```

## Run bot
```bash
cd backend
python run_bot.py
```

## Docker
```bash
docker compose up --build
```

## Tests
```bash
cd backend
pytest -q
```

Copy `.env.example` to `.env` and fill secrets.
