from backend.parsers import normalize_text
from embeddings import get_embedding, cosine_similarity
from fuzzywuzzy import fuzz
import re
from llm_feedback import generate_feedback_with_llm
COMMON_SKILLS = ['python','java','c++','react','node','sql','aws','docker','kubernetes','ml','django','flask','tensorflow','pytorch']
def extract_skills_from_jd(jd_text):
    text = jd_text.lower(); skills=[]
    m = re.search(r'(skills|requirements|must have|must-have)[:\-\s]\s*([^\n]+)', text)
    if m: skills += [s.strip() for s in re.split('[,;\n]', m.group(2)) if s.strip()]
    for f in COMMON_SKILLS:
        if f in text and f not in skills: skills.append(f)
    return list(dict.fromkeys(skills))
def hard_match_score(resume_text, jd_text):
    res_norm = normalize_text(resume_text); skills = extract_skills_from_jd(jd_text)
    matched=[]; missing=[]
    for sk in skills:
        sk_n = normalize_text(sk); ratio = fuzz.partial_ratio(sk_n, res_norm)
        if sk_n in res_norm or ratio>=75: matched.append(sk)
        else: missing.append(sk)
    hard_score = 100.0*len(matched)/max(1,len(skills)) if skills else 0.0
    return hard_score, matched, missing
def semantic_score(resume_text, jd_text):
    e1 = get_embedding(resume_text); e2 = get_embedding(jd_text)
    sim = cosine_similarity(e1,e2); score = max(0.0, min(100.0,(sim+1)/2*100))
    phrases=[p.strip() for p in jd_text.split('.') if p.strip()][:8]; hits=[]
    for p in phrases:
        for w in p.split():
            if w.lower() in resume_text.lower(): hits.append(p); break
        if len(hits)>=5: break
    return score, hits
def generate_feedback(missing_skills, matched, resume_text, jd_text):
    fb = generate_feedback_with_llm(resume_text, jd_text, missing_skills, matched)
    if fb: return fb, True
    feedback=[]
    if missing_skills: feedback.append("Missing / weak skills: "+", ".join(missing_skills)); feedback.append("Recommendation: Add short projects...")
    else: feedback.append("All listed JD skills appear...")
    if 'tensorflow' in jd_text.lower() and 'tensorflow' not in resume_text.lower(): feedback.append("If applying to ML roles...")
    return feedback, False
def evaluate_resume_for_jd(resume_text, jd_text, weights=(0.6,0.4)):
    hard, matched, missing = hard_match_score(resume_text, jd_text)
    sem, hits = semantic_score(resume_text, jd_text)
    final = weights[0]*hard + weights[1]*sem
    verdict="Low"
    if final>=75: verdict="High"
    elif final>=50: verdict="Medium"
    feedback, used = generate_feedback(missing, matched, resume_text, jd_text)
    details={"hard_matches": matched, "missing_skills": missing, "semantic_hits": hits, "breakdown":{"hard_score":hard,"semantic_score":sem}, "feedback":feedback, "llm_used": bool(used)}
    return float(final), verdict, details
