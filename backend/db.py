import sqlite3, os, json
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        jd_text TEXT,
        location TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        location TEXT,
        raw_text TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        job_id INTEGER,
        score REAL,
        verdict TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
def add_job(title, jd_text, location=""):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO jobs (title,jd_text,location) VALUES (?,?,?)", (title, jd_text, location))
    conn.commit(); cid = cur.lastrowid; conn.close(); return cid
def get_jobs():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM jobs ORDER BY id DESC")
    rows = cur.fetchall(); conn.close(); return rows
def add_resume(name, email, location, raw_text):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO resumes (name,email,location,raw_text) VALUES (?,?,?,?)", (name,email,location,raw_text))
    conn.commit(); rid = cur.lastrowid; conn.close(); return rid
def add_evaluation(resume_id, job_id, score, verdict, details_dict):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO evaluations (resume_id,job_id,score,verdict,details) VALUES (?,?,?,?,?)",
                (resume_id, job_id, score, verdict, json.dumps(details_dict)))
    conn.commit(); eid = cur.lastrowid; conn.close(); return eid
def get_evaluations_for_job(job_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT e.*, r.name as candidate_name, r.email as candidate_email, r.location as candidate_location FROM evaluations e JOIN resumes r ON r.id=e.resume_id WHERE e.job_id=? ORDER BY e.score DESC", (job_id,))
    rows = cur.fetchall(); conn.close(); return rows
def get_resume(resume_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM resumes WHERE id=?", (resume_id,))
    r = cur.fetchone(); conn.close(); return r
