# How to run Knowledge Dungeon

You need Python 3.11+ and Node 20+. Run every command from the project folder unless a step says otherwise:

```
cd C:\Users\Rushabh\Downloads\Projects\knowledge-dungeon
```

## 1. One-time setup

Install the Python packages:

```
pip install -r requirements.txt
```

Download the training data (about 1.6 MB):

```
python -m ml.download
```

Train the knowledge tracer. It takes about 15 seconds; add `--no-dkt` to skip the slower DKT benchmark:

```
python -m ml.train
```

Install the frontend packages:

```
cd frontend
npm install
cd ..
```

Add your LLM key. Copy `.env.example` to `.env` and fill in your Groq key:

```
LLM_API_KEY=your-groq-key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-120b
```

Without a key, only the demo dungeon works.

## 2. Start the app (every time)

You need two terminals.

**Terminal 1: backend**, from the project folder:

```
python -m uvicorn backend.app.main:app --port 8000
```

**Terminal 2: frontend**, from the `frontend` folder:

```
cd frontend
npm run dev
```

Then open **http://localhost:3000** in your browser.

To stop either server, press `Ctrl + C` in its terminal.

## 3. Check it's working

Open http://localhost:8000/api/health. It should show `"llm": true`. If it shows `false`, the key in `.env` isn't being read.

## 4. Optional: rebuild the sample PDFs

The sample books are in `samples/pdf/`. To regenerate them from their Markdown source:

```
python samples/build_books.py
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `No module named 'backend'` | You're not in the project folder. `cd` into it first. |
| `Could not read package.json` | Run `npm run dev` inside the `frontend` folder. |
| `address already in use` / port 3000 or 8000 busy | Another copy is already running. Stop it with `Ctrl + C`, or just use the one that's running. |
| The site says it can't reach the game server | The backend (Terminal 1) isn't running. |
