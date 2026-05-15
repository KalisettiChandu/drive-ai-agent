# Drive AI Agent

Conversational (LLM-assisted) Google Drive search agent.

- **Backend:** FastAPI (Python)
- **Frontend:** Streamlit
- **Drive Integration:** Google Drive API via **Service Account**
- **LLM:** Gemini via `langchain-google-genai` (with a safe fallback query generator if the LLM is unavailable)

## What it does

- Accepts a natural-language request (e.g., “Find PDFs”, “Find daily reports”, “Find invoices from last week”).
- Translates it into a Google Drive `files.list` **`q`** query string.
- Executes the query via Drive API and returns matching files with `webViewLink`.

## Project structure

- `backend/` – FastAPI app and Drive search logic
- `frontend/` – Streamlit chat UI
- `credentials.json` – **Service account** credentials (ignored by git)

## Prerequisites

- Python 3.10+ recommended
- A Google Cloud project with **Google Drive API enabled**
- A **Service Account** JSON key downloaded as `credentials.json`
- A Google Drive folder shared with that service account

## 1) Google Drive setup (Service Account)

1. Create a Service Account in Google Cloud.
2. Enable **Google Drive API**.
3. Create a JSON key and download it.
4. Place it at repo root as `credentials.json`.
5. In Google Drive:
   - Copy the sample folder into your Drive.
   - Share the copied folder with the service account `client_email` from `credentials.json`.
   - Copy the folder id (the part after `/folders/` in the URL).

## 2) Local development

### Create and activate venv

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install -r backend/requirements.txt
python -m pip install -r frontend/requirements.txt
```

### Configure environment

Create / edit `backend/.env`:

```env
GOOGLE_API_KEY=...               # optional (Gemini). If missing/quota blocked, fallback is used.
GEMINI_MODEL=gemini-2.0-flash
DRIVE_FOLDER_ID=...              # recommended: restrict search to a single folder
```

> Notes:
> - `DRIVE_FOLDER_ID` is strongly recommended to avoid searching your entire Drive.
> - If Gemini quota is exceeded, the backend returns `usedFallback=true` and still works.

### Run backend

```powershell
cd backend
uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

### Run frontend

```powershell
cd frontend
streamlit run app.py
```

Frontend runs at `http://localhost:8501`.

## 3) API contract

### POST `/chat`

Request:

```json
{ "message": "Find PDFs" }
```

Response:

```json
{
  "query": "mimeType='application/pdf'",
  "files": [{"id":"...","name":"...","mimeType":"...","webViewLink":"..."}],
  "usedFallback": true
}
```

## 4) Deployment (Render)

This repo is designed to deploy as **two services**:

- `drive-ai-backend` (FastAPI)
- `drive-ai-frontend` (Streamlit)

### 4.1 Deploy backend service

Render → New → **Web Service**

- **Root Directory:** `backend`
- **Build Command:**
  - `pip install -r requirements.txt`
- **Start Command:**
  - `uvicorn main:app --host 0.0.0.0 --port $PORT`

Set environment variables in Render:

- `DRIVE_FOLDER_ID` = your shared folder id
- `GOOGLE_SERVICE_ACCOUNT_JSON` = paste the full contents of `credentials.json` as a JSON string
- Optional (Gemini):
  - `GOOGLE_API_KEY`
  - `GEMINI_MODEL`

> In production you should **not** ship `credentials.json` as a file. The backend supports `GOOGLE_SERVICE_ACCOUNT_JSON` for this.

### 4.2 Deploy frontend service

Render → New → **Web Service**

- **Root Directory:** `frontend`
- **Build Command:**
  - `pip install -r requirements.txt`
- **Start Command:**
  - `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`

Set environment variables in Render:

- `BACKEND_URL` = your backend Render URL, e.g. `https://drive-ai-backend.onrender.com`

## Troubleshooting

### Streamlit shows JSON decode error

This usually happens when the backend returns a non-JSON error. The frontend is hardened to show the backend error message and status code.

### Gemini quota / 429 RESOURCE_EXHAUSTED

If Gemini quota is blocked, the agent automatically uses a fallback query generator.
To restore LLM behavior, enable quota/billing for Gemini or switch to another LLM provider.

---

If you want, I can add an OpenAI/Groq LLM switch via env vars for production reliability.
