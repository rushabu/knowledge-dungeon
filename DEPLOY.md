# Deploying Knowledge Dungeon

The backend (FastAPI) goes on **Render** and the frontend (Next.js) on **Vercel**, both on free plans.
Deploy the backend first, because the frontend needs its URL.

## 1. Backend on Render

1. Sign in at https://render.com with GitHub.
2. **New → Blueprint**, pick the `knowledge-dungeon` repo. Render reads [`render.yaml`](render.yaml).
3. It asks for two values:
   - `LLM_API_KEY`: your Groq key.
   - `CORS_ORIGINS`: your Vercel URL (e.g. `https://knowledge-dungeon.vercel.app`). If you don't
     have it yet, enter `http://localhost:3000` and change it after step 2. It's only used if you
     turn on direct mode (see below).
4. **Apply.** The first build takes a few minutes.
5. Open `https://<your-service>.onrender.com/api/health`. It should show `"ok": true, "llm": true`.

The server installs only [`backend/requirements.txt`](backend/requirements.txt), without PyTorch.

## 2. Frontend on Vercel

1. Sign in at https://vercel.com with GitHub.
2. **Add New → Project**, import the `knowledge-dungeon` repo.
3. Set **Root Directory** to `frontend`. Vercel detects Next.js.
4. Under **Environment Variables**, add:
   - `BACKEND_URL` = `https://<your-service>.onrender.com` (no trailing slash)
5. **Deploy.**

The site forwards every `/api/...` request to Render, so the browser only talks to Vercel.
`BACKEND_URL` is read at build time: if you change it, **redeploy**.

## 3. Check it

Open the Vercel URL, click **Try the demo**, and play a fight. Then upload one of the PDFs in
`samples/pdf/`.

## Things to know (free plans)

- **Render sleeps after 15 minutes idle.** The next visit waits about a minute while it wakes.
  Open the site once before a demo or judging.
- **Render's free disk isn't permanent.** Uploaded dungeons and progress are wiped when the
  service restarts, redeploys or sleeps. The demo dungeon rebuilds instantly. To keep data, add a
  paid persistent disk on Render and set `DB_PATH` to a file on it (e.g. `/data/dungeon.db`).
- **Updates:** pushing to `main` redeploys both automatically.

## Optional: direct mode

If large PDF uploads fail through Vercel, let the browser call Render directly:

1. On Vercel, add `NEXT_PUBLIC_API_URL` = `https://<your-service>.onrender.com` and redeploy.
2. On Render, make sure `CORS_ORIGINS` is your exact Vercel URL.

## Environment variables

| Where | Name | Value |
|---|---|---|
| Render | `LLM_API_KEY` | your Groq key (secret) |
| Render | `LLM_BASE_URL` | `https://api.groq.com/openai/v1` (set by render.yaml) |
| Render | `LLM_MODEL` | `openai/gpt-oss-120b` (set by render.yaml) |
| Render | `CORS_ORIGINS` | your Vercel URL |
| Render | `DB_PATH` | optional, only with a persistent disk |
| Vercel | `BACKEND_URL` | your Render URL |
| Vercel | `NEXT_PUBLIC_API_URL` | optional, direct mode only |
