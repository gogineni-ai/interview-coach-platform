# Interview Coach Platform

A full-stack interview practice platform with:

- Login / registration
- Resume upload and text extraction
- Resume analysis
- Mock-interview question generation
- Live microphone transcription in the browser
- Automatic question detection
- Resume-grounded answer coaching
- Practice-mode guardrails

## Important use boundary

This project is intended for mock interviews, interview preparation, and disclosed coaching.
It does not provide covert answer generation during a real hiring interview.

## Stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: SQLite
- Authentication: JWT
- Resume parsing: PDF, DOCX, TXT

## Run backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## AI integration

The backend contains a provider abstraction in `ai_service.py`.
By default it uses a deterministic local fallback so the app works without an API key.

You can later replace `generate_answer()` and `analyze_resume()` with your preferred LLM provider.

## Browser microphone support

Live transcription uses the browser Web Speech API when available.
Chrome / Edge usually provide the best support.

## Production upgrades

For a production deployment, replace:
- SQLite with PostgreSQL
- Local file storage with object storage
- Dev JWT secret with a secure environment secret
- Browser speech recognition with a production STT service if required
