# llm_feedback.py
import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# New OpenAI client for openai>=1.0.0
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OpenAI = None
    OPENAI_AVAILABLE = False

OPENAI_KEY = os.getenv("OPENAI_API_KEY")  # can be None

def _build_prompt(resume_text: str, jd_text: str, missing_skills: list) -> str:
    # Keep prompt concise (avoid sending huge text). Send first N chars of resume/jd.
    resume_snippet = (resume_text or "")[:1500]
    jd_snippet = (jd_text or "")[:1500]
    missing = ", ".join(missing_skills) if missing_skills else "None"
    prompt = (
        "You are a concise, practical career coach. "
        "Given a job description and a candidate resume, produce up to 6 short, actionable improvement "
        "suggestions the candidate can implement quickly (e.g., add project X, learn library Y, fix resume formatting). "
        "Prioritize concrete steps and specific technologies. Output as short bullet points (no numbering).\n\n"
        f"Job description (first 1500 chars):\n{jd_snippet}\n\n"
        f"Resume (first 1500 chars):\n{resume_snippet}\n\n"
        f"Missing skills detected: {missing}\n\n"
        "Return only the bullet points (one per line)."
    )
    return prompt

def generate_feedback_with_llm(
    resume_text: str,
    jd_text: str,
    missing_skills: list,
    matched_skills: list,
    max_tokens: int = 256,
    model: str = "gpt-3.5-turbo"
) -> Optional[List[str]]:
    """
    Call OpenAI Chat Completions using the new OpenAI client (>=1.0).
    Returns: list of feedback bullet strings, or None if unable to call LLM.
    """
    if not OPENAI_KEY:
        logger.info("OPENAI_API_KEY not set; skipping LLM feedback.")
        return None
    if not OPENAI_AVAILABLE or OpenAI is None:
        logger.info("OpenAI SDK not available; skipping LLM feedback.")
        return None

    try:
        client = OpenAI(api_key=OPENAI_KEY)
    except TypeError:
        # Some OpenAI builds take no api_key argument and rely on env var
        client = OpenAI()

    prompt = _build_prompt(resume_text, jd_text, missing_skills)

    try:
        # Create a chat completion
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful career coach who writes concise actionable feedback."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.2
        )
        # resp.choices[0].message.content is the text (new SDK)
        text = ""
        try:
            text = resp.choices[0].message.content
        except Exception:
            # Some SDK versions return slightly different shapes; fallback:
            text = getattr(resp.choices[0], "message", {}).get("content", "") if resp.choices else ""

        if not text:
            logger.info("LLM returned empty text.")
            return None

        # Normalize into bullet lines
        lines = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            # strip leading bullet markers (-, *, •, or numbering)
            if line[0] in ("-", "*", "•"):
                line = line[1:].strip()
            # remove leading numbers like "1. " or "1) "
            if len(line) > 2 and line[0].isdigit() and line[1] in (".", ")"):
                line = line[2:].strip()
            lines.append(line)
        # dedupe and limit
        seen = set()
        out = []
        for l in lines:
            if l.lower() in seen:
                continue
            seen.add(l.lower())
            out.append(l)
            if len(out) >= 8:
                break
        return out if out else None

    except Exception as ex:
        logger.exception("LLM call failed")
        return None

