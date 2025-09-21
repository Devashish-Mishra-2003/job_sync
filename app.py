# app.py — Full Streamlit UI (cleaned & fixed preview behavior)
import os
import streamlit as st
import requests
import json
from utils import parse_name_email_from_text

st.set_page_config(page_title="JobSync", layout="wide")

# ---------------- Sidebar ----------------
st.sidebar.header("Settings")

DEFAULT_BACKEND = os.getenv("BACKEND_URL", "https://jobsync-backend-kw2x.onrender.com")
backend_url = st.sidebar.text_input("Backend URL", value=DEFAULT_BACKEND)

role = st.sidebar.selectbox("Role", ["Student", "Placement Team"])
use_ai = st.sidebar.checkbox("Enable AI-powered feedback", value=False)

with st.sidebar.expander("Advanced (backend override)", expanded=False):
    be_override = st.text_input("Override Backend URL", value="")
    if be_override:
        if st.button("Apply override"):
            backend_url = be_override
            st.sidebar.success("Backend URL override applied (will be used during this session).")

# ---------------- Title ----------------
st.markdown(
    "<h1 style='font-size:2.5em; font-weight:bold;'>Job<span style='color:blue;'>Sync</span></h1>",
    unsafe_allow_html=True
)

# ---------------- API helpers ----------------
def api_get(path):
    url = backend_url.rstrip("/") + path
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def api_post(path, data=None):
    url = backend_url.rstrip("/") + path
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()

def api_post_file(path, files=None, data=None):
    url = backend_url.rstrip("/") + path
    r = requests.post(url, files=files, data=data)
    r.raise_for_status()
    return r.json()

# ---------------- Student view ----------------
if role == "Student":
    st.header("Available Job Postings")
    try:
        jobs = api_get("/jobs")
    except Exception as e:
        st.error(f"Could not fetch jobs from backend: {e}")
        jobs = []

    if not jobs:
        st.info("No jobs available. Placement team can add JDs in the Placement Team view.")
    for job in jobs:
        job_id = job.get("id")
        title = job.get("title", "Untitled")
        loc = job.get("location", "")
        with st.expander(f"{title} — {loc} (Job ID: {job_id})"):
            # show a safe preview: JD text comes from backend so it's safe
            st.write(job.get("jd_text", "")[:800] + ("..." if len(job.get("jd_text", "")) > 800 else ""))
            uploaded = st.file_uploader(
                f"Upload your resume for Job {job_id}",
                type=['pdf', 'docx', 'txt', 'doc'],
                key=f"up_{job_id}"
            )

            if uploaded is not None:
                # read bytes for sending to backend
                raw_bytes = uploaded.read()
                parsed_name, parsed_email = "", ""
                text_preview = ""
                try:
                    # try a quick UTF-8 decode for preview only (works for txt and some docx exports)
                    text_preview = raw_bytes.decode('utf-8', errors='ignore')[:1000]
                    parsed_name, parsed_email = parse_name_email_from_text(text_preview)
                except Exception:
                    parsed_name, parsed_email = "", ""

                lower = (uploaded.name or "").lower()
                if lower.endswith(".txt"):
                    # show actual text preview for text files
                    st.code(text_preview or "<no text preview>")
                else:
                    # For binary formats (PDF/DOCX) we avoid printing raw bytes.
                    # Show a simple informative message — server will do the authoritative parsing.
                    st.info("File uploaded — preview unavailable for this file type. The backend will extract and parse the resume.")

                name = st.text_input("Name", value=parsed_name or "", key=f"name_{job_id}")
                email = st.text_input("Email", value=parsed_email or "", key=f"email_{job_id}")
                location_input = st.text_input("Your Location", value="", key=f"loc_{job_id}")

                if st.button("Submit & Evaluate", key=f"eval_{job_id}"):
                    if not name or not email:
                        st.error("Please provide name and email before evaluating.")
                    else:
                        files = {"file": (uploaded.name, raw_bytes)}
                        data = {"name": name, "email": email, "location": location_input, "use_ai": str(use_ai)}
                        try:
                            resp = api_post_file("/resumes", files=files, data=data)
                            resume_id = resp.get("resume_id")
                            # call sync evaluate endpoint
                            resp2 = api_post("/evaluate_sync", data={"resume_id": resume_id, "job_id": job_id, "use_ai": str(use_ai)})
                            score = resp2.get("score")
                            verdict = resp2.get("verdict")
                            details = resp2.get("details", {}) or {}
                            st.success(f"Score: {score:.1f} — Verdict: {verdict}")
                            if isinstance(details, str):
                                try:
                                    details = json.loads(details)
                                except Exception:
                                    details = {}
                            if details.get('llm_used', False):
                                st.markdown("*AI-powered feedback was used for this evaluation.*")
                            else:
                                if use_ai:
                                    st.info("AI was requested but backend did not return AI feedback (no key or quota). Showing fallback feedback.")
                            st.markdown("**Feedback:**")
                            for f in details.get('feedback', []):
                                st.write("-", f)
                        except Exception as e:
                            st.error(f"Evaluation failed: {e}")

# ---------------- Placement Team view ----------------
else:
    st.header("Placement Team Dashboard")

    st.subheader("1) Upload a Job Description")
    with st.form("add_jd"):
        title = st.text_input("Job Title")
        location = st.text_input("Job Location (city / remote)")
        jd_file = st.file_uploader(
            "Job Description (txt, pdf, docx) — upload .txt or .pdf/.docx for full JD",
            type=['txt', 'pdf', 'docx', 'doc'],
            key="jd_upload"
        )
        if st.form_submit_button("Add Job"):
            if not title or not jd_file:
                st.error("Provide a title and a JD text file.")
            else:
                try:
                    # read bytes for backend
                    jd_bytes = jd_file.read()

                    # Here is the fix: we no longer attempt to preview the file
                    # on the client side. We let the backend do the authoritative
                    # parsing and show the result from the database later.

                    st.info("File uploaded. The backend will extract and parse the JD.")

                    files = {"jd_file": (jd_file.name, jd_bytes)}
                    resp = api_post_file("/jobs", files=files, data={"title": title, "location": location})
                    st.success(f"Job added (id={resp.get('job_id')})")
                except Exception as e:
                    st.error(f"Failed to add job: {e}")

    st.subheader("2) View job evaluations")
    try:
        jobs = api_get("/jobs")
    except Exception as e:
        st.error(f"Could not fetch jobs from backend: {e}")
        jobs = []

    if not jobs:
        st.info("No jobs available.")
    else:
        sel = st.selectbox("Select job", options=jobs, format_func=lambda x: f"{x.get('title')} — {x.get('location')}")
        job_id = int(sel.get('id'))
        st.markdown("**Job Description (preview):**")
        st.write(sel.get('jd_text', '')[:1000])

        # filters
        min_score = st.slider("Min score", 0, 100, 0)
        location_filter = st.text_input("Filter by candidate location (substring)", value="")

        try:
            evals = api_get(f"/evaluations/{job_id}")
        except Exception as e:
            st.error(f"Failed to get evaluations: {e}")
            evals = []

        # apply filters
        filtered = []
        for e in evals:
            try:
                if float(e.get('score', 0) or 0) < min_score:
                    continue
                if location_filter and location_filter.lower() not in (e.get('candidate_location') or "").lower():
                    continue
                filtered.append(e)
            except Exception:
                continue

        st.write(f"{len(filtered)} candidates found (after filters)")

        if len(filtered):
            for e in filtered:
                st.markdown("---")
                st.subheader(f"{e.get('candidate_name')} — Score: {float(e.get('score',0)):.1f} — Verdict: {e.get('verdict')}")
                st.write("Location:", e.get('candidate_location'))
                st.write("Email:", e.get('candidate_email'))

                # details may be stored as JSON string in DB — handle both
                details = {}
                try:
                    details = json.loads(e.get('details') or "{}")
                except Exception:
                    details = e.get('details') or {}

                with st.expander("Details & Feedback"):
                    hard_matches = details.get('hard_matches', [])
                    missing = details.get('missing_skills', [])
                    semantic_hits = details.get('semantic_hits', [])
                    feedback_lines = details.get('feedback', [])

                    st.markdown("**Hard matches:**")
                    if hard_matches:
                        st.write(", ".join(hard_matches))
                    else:
                        st.write("None")

                    st.markdown("**Missing skills / items:**")
                    if missing:
                        st.write(", ".join(missing))
                    else:
                        st.write("None")

                    if semantic_hits:
                        st.markdown("**Relevant JD phrases that appear to match the resume:**")
                        for phrase in semantic_hits:
                            display_text = str(phrase).strip()
                            if len(display_text) > 200:
                                display_text = display_text[:200].rsplit(" ", 1)[0] + "..."
                            st.write(f"- {display_text}")
                    else:
                        st.markdown("**Semantic hits:** None")

                    st.markdown("**Actionable feedback (summary):**")
                    if feedback_lines:
                        for fl in feedback_lines:
                            st.write("- " + str(fl))
                    else:
                        st.write("No feedback available.")

            # export CSV button
            if st.button("Export current view to CSV"):
                try:
                    import pandas as pd, io
                    rows = []
                    for e in filtered:
                        d = {}
                        try:
                            d = json.loads(e.get('details') or "{}")
                        except:
                            d = {}
                        rows.append({
                            "candidate_name": e.get('candidate_name'),
                            "email": e.get('candidate_email'),
                            "location": e.get('candidate_location'),
                            "score": e.get('score'),
                            "verdict": e.get('verdict'),
                            "missing": ",".join(d.get('missing_skills', []))
                        })
                    df = pd.DataFrame(rows)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="Download CSV", data=csv, file_name=f"evaluations_job_{job_id}.csv")
                except Exception as ex:
                    st.error(f"Export failed: {ex}")