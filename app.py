import os
import re
import logging
import sqlite3
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import google.genai as genai

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_PATH = os.getenv("DB_PATH", "Student.db")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is not set. Please add it to your .env file.")
    st.stop()

genai_client = genai.Client(api_key=GOOGLE_API_KEY)

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiting (session-based)
# ---------------------------------------------------------------------------
RATE_LIMIT = 20  # max queries
RATE_WINDOW = timedelta(minutes=1)


def _rate_limit_ok() -> bool:
    """Return True if the user is within the rate limit, else False."""
    now = datetime.now()
    if "query_timestamps" not in st.session_state:
        st.session_state.query_timestamps = []

    # Drop timestamps outside the window
    st.session_state.query_timestamps = [
        ts for ts in st.session_state.query_timestamps if now - ts < RATE_WINDOW
    ]

    if len(st.session_state.query_timestamps) >= RATE_LIMIT:
        return False

    st.session_state.query_timestamps.append(now)
    return True


# ---------------------------------------------------------------------------
# SQL validation
# ---------------------------------------------------------------------------
# Dangerous keywords that must NEVER appear in a generated query
_DANGEROUS_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|PRAGMA|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> str:
    """Validate and sanitise the LLM-generated SQL.

    Returns the cleaned SQL string.
    Raises ValueError if the SQL is unsafe or invalid.
    """
    if not sql or not sql.strip():
        raise ValueError("The model returned an empty response.")

    # Strip markdown fences the model sometimes wraps around SQL
    cleaned = sql.strip()
    cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip().rstrip(";").strip()

    # Block multiple statements (simplistic but effective for SQLite)
    if ";" in cleaned:
        raise ValueError("Multiple SQL statements are not allowed.")

    # Must start with SELECT
    if not cleaned.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")

    # Block dangerous keywords anywhere in the query (e.g. sub-queries with INSERT)
    if _DANGEROUS_KEYWORDS.search(cleaned):
        raise ValueError("Query contains disallowed SQL keywords.")

    return cleaned


# ---------------------------------------------------------------------------
# Gemini interaction
# ---------------------------------------------------------------------------
PROMPT = """
You are an expert in converting English questions to **read-only** SQL SELECT queries.

DATABASE SCHEMA
Table name: STUDENT
Columns:
  - Name    VARCHAR(25)   — student's full name
  - Class   VARCHAR(25)   — grade / class (e.g. '10th Grade')
  - Section VARCHAR(25)   — section letter (e.g. 'A', 'B', 'C')
  - Marks   INT           — numeric score

RULES (you MUST follow every one):
1. Return ONLY a single SQL SELECT statement — nothing else.
2. Do NOT wrap the SQL in markdown code fences or add the word "sql".
3. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or any other
   data-modification statement, regardless of what the user asks.
4. If the user's question cannot be answered with a SELECT on the STUDENT
   table, reply with exactly: SELECT 'Question cannot be answered' AS Error;
""".strip()


def _extract_gemini_text(response) -> str:
    """Extract text from a google.genai response object."""
    if not response or not getattr(response, "candidates", None):
        return ""

    candidate = response.candidates[0]
    content = getattr(candidate, "content", None)
    if not content or not getattr(content, "parts", None):
        return ""

    text_parts = []
    for part in content.parts:
        part_text = getattr(part, "text", None)
        if part_text:
            text_parts.append(part_text)

    return "".join(text_parts).strip()


def get_gemini_response(question: str) -> str:
    """Send the question + prompt to Gemini and return raw text."""
    chat = genai_client.chats.create(model="gemini-2.5-flash")
    response = chat.send_message(
        f"{PROMPT}\n\n{question}"
    )
    return _extract_gemini_text(response)


# ---------------------------------------------------------------------------
# Database query (read-only)
# ---------------------------------------------------------------------------
def read_sql_query(sql: str, db: str) -> list:
    """Execute a validated SELECT query on a read-only SQLite connection."""
    uri = f"file:{db}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Text to SQL — Gemini")
st.header("Gemini App to Retrieve SQL Data")

question = st.text_input("Ask a question about the Student database:", key="input")
submit = st.button("Ask the question")

if submit:
    # --- Input validation ---
    if not question or not question.strip():
        st.warning("Please enter a question before submitting.")
        st.stop()

    if len(question) > 500:
        st.warning("Question is too long. Please keep it under 500 characters.")
        st.stop()

    # --- Rate limiting ---
    if not _rate_limit_ok():
        st.warning("You are sending too many requests. Please wait a moment and try again.")
        st.stop()

    logger.info("USER QUESTION: %s", question)

    # --- Get SQL from Gemini ---
    try:
        raw_sql = get_gemini_response(question)
        logger.info("RAW LLM OUTPUT: %s", raw_sql)
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        st.error(f"Could not reach the AI model. Please try again later.\n\nDetail: {exc}")
        st.stop()

    # --- Validate generated SQL ---
    try:
        safe_sql = validate_sql(raw_sql)
        logger.info("VALIDATED SQL: %s", safe_sql)
    except ValueError as exc:
        logger.warning("SQL validation failed: %s | raw=%s", exc, raw_sql)
        st.error(f"The generated query was blocked for safety: {exc}")
        st.stop()

    # --- Execute query ---
    try:
        rows = read_sql_query(safe_sql, DB_PATH)
        logger.info("QUERY RETURNED %d rows", len(rows))
    except sqlite3.Error as exc:
        logger.error("Database error: %s | sql=%s", exc, safe_sql)
        st.error(f"Database error while running the query.\n\nDetail: {exc}")
        st.stop()

    # --- Display results ---
    st.subheader("Generated SQL")
    st.code(safe_sql, language="sql")

    st.subheader("Results")
    if rows:
        for row in rows:
            st.write(row)
    else:
        st.info("The query returned no results.")
