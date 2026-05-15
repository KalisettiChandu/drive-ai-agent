from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone
import re

from drive_service import search_drive

load_dotenv()


def _build_fallback_query(user_input: str) -> str:
    text = (user_input or "").strip().lower()
    conditions: list[str] = []

    # Basic type intent
    if "pdf" in text or text.endswith(".pdf"):
        conditions.append("mimeType='application/pdf'")
    elif any(k in text for k in ["image", "images", "png", "jpg", "jpeg", "gif", "webp"]):
        conditions.append("mimeType contains 'image/'")
    elif any(k in text for k in ["spreadsheet", "spreadsheets", "sheet", "sheets", "xlsx", "csv"]):
        # Google Sheets
        conditions.append("mimeType='application/vnd.google-apps.spreadsheet'")
    elif any(k in text for k in ["doc", "docs", "document", "documents"]):
        conditions.append("mimeType='application/vnd.google-apps.document'")

    # Keyword intent
    if "invoice" in text or "invoices" in text:
        conditions.append("fullText contains 'invoice'")
    if "report" in text or "reports" in text:
        conditions.append("name contains 'report'")

    # Date intent (very small set; avoids overfitting)
    now = datetime.now(timezone.utc)
    if "last week" in text:
        since = now - timedelta(days=7)
        conditions.append(f"modifiedTime > '{since.isoformat().replace('+00:00', 'Z')}'")
    elif "yesterday" in text:
        since = now - timedelta(days=1)
        conditions.append(f"modifiedTime > '{since.isoformat().replace('+00:00', 'Z')}'")
    elif "today" in text:
        since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        conditions.append(f"modifiedTime > '{since.isoformat().replace('+00:00', 'Z')}'")

    # Quoted phrase -> name contains
    m = re.search(r"['\"]([^'\"]{2,})['\"]", user_input or "")
    if m:
        phrase = m.group(1).replace("'", "\\'")
        conditions.append(f"name contains '{phrase}'")

    # Default: broad search in name
    if not conditions and user_input:
        safe = user_input.strip().replace("'", "\\'")
        conditions.append(f"name contains '{safe}'")

    return " and ".join(conditions) if conditions else "trashed=false"


def _get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        google_api_key=api_key,
    )


def ask_agent(user_input):

    prompt = f"""
    You are a Google Drive search assistant.

    Convert the user's request into a valid Google Drive API q query.

    Examples:

    User: Find PDFs
    Query: mimeType='application/pdf'

    User: Find images
    Query: mimeType contains 'image/'

    User: Find spreadsheets
    Query: mimeType='application/vnd.google-apps.spreadsheet'

    User: Find invoices
    Query: fullText contains 'invoice'

    User: Find reports
    Query: name contains 'report'


    IMPORTANT:
    Only return the query.
    Do not explain anything.

    User Request:
    {user_input}
    """

    llm = _get_llm()
    drive_query = ""
    used_fallback = False
    if llm is None:
        used_fallback = True
        drive_query = _build_fallback_query(user_input)
    else:
        try:
            response = llm.invoke(prompt)
            drive_query = (response.content or "").strip()

            # Keep the contract simple: a single Drive API q string.
            # Models sometimes wrap in code fences or prefix with "Query:".
            drive_query = drive_query.strip("` ")
            if drive_query.lower().startswith("query:"):
                drive_query = drive_query.split(":", 1)[1].strip()
        except Exception:
            used_fallback = True
            drive_query = _build_fallback_query(user_input)

    print("Generated Query:", drive_query)

    files = search_drive(drive_query)

    return {
        "query": drive_query,
        "files": files,
        "usedFallback": used_fallback,
    }