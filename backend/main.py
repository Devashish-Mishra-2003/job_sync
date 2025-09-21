from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, io, json, os, sys
# Ensure project root is on sys.path so imports like 'db' work when running uvicorn
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.parsers import extract_text
from backend.db import init_db, add_job, get_jobs, add_resume, add_evaluation, get_evaluations_for_job, get_resume
from backend.scoring import evaluate_resume_for_jd
from embeddings import get_embedding
from vectorstore import SimpleVectorStore
app = FastAPI(title="Automated Resume Relevance API")
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
init_db(); store = SimpleVectorStore(path='vectorstore_api')
def _get_job_by_id(job_id: int):
    for row in get_jobs():
        r = dict(row)
        if int(r.get('id'))==int(job_id): return r
    return None
@app.post('/jobs')
async def create_job(title: str = Form(...), location: str = Form(''), jd_file: UploadFile = File(...)):
     try:
        content = await jd_file.read()
        # build a small file-like object that our parsers.extract_text expects
        class FObj:
            def __init__(self, b, filename, content_type):
                self._b = b
                self.name = filename
                self.type = content_type
            def read(self):
                return self._b
        fobj = FObj(content, jd_file.filename or "", jd_file.content_type or "")
        jd_text = extract_text(fobj)
        if not jd_text:
            # If extract_text returned empty, try naive decode for txt fallback
            try:
                jd_text = content.decode('utf-8', errors='ignore')
            except:
                jd_text = ""
        if not title or not jd_text:
            raise ValueError("Missing title or JD text after parsing.")
        job_id = add_job(title, jd_text, location)
        return {"job_id": job_id}
     except Exception as e:
        # return a helpful error to the client and log server side
        import traceback, sys
        tb = traceback.format_exc()
        print("create_job error:", tb, file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Failed to add job: {str(e)}")
@app.get('/jobs')
def list_jobs(): return [dict(r) for r in get_jobs()]
@app.post('/resumes')
async def upload_resume(file: UploadFile = File(...), name: str = Form(''), email: str = Form(''), location: str = Form('')):
    content = await file.read()
    class _F: 
        def __init__(self,b,fn,ct): self._b=b; self.name=fn; self.type=ct
        def read(self): return self._b
    fobj = _F(content, file.filename, file.content_type)
    raw_text = extract_text(fobj); rid = add_resume(name, email, location, raw_text); return {'resume_id': rid}
@app.post('/evaluate_sync')
def evaluate_sync(resume_id: int = Form(...), job_id: int = Form(...)):
    job = _get_job_by_id(job_id); 
    if job is None: raise HTTPException(status_code=404, detail='job not found')
    r = get_resume(resume_id)
    if r is None: raise HTTPException(status_code=404, detail='resume not found')
    score, verdict, details = evaluate_resume_for_jd(r['raw_text'], job['jd_text'])
    add_evaluation(resume_id, job_id, score, verdict, details)
    try:
        vec = get_embedding(r['raw_text']); store.add(vec, {'resume_id': resume_id, 'job_id': job_id, 'name': r['name'], 'email': r['email'], 'location': r['location']})
    except Exception as ex:
        print('embedding error', ex)
    return {'score': score, 'verdict': verdict, 'details': details}
@app.get('/evaluations/{job_id}')
def evaluations_for_job(job_id: int): return [dict(r) for r in get_evaluations_for_job(job_id)]
@app.get('/search_from_job/{job_id}')
def search_from_job(job_id: int, top_k: int = 5):
    job = _get_job_by_id(job_id); 
    if job is None: raise HTTPException(status_code=404, detail='job not found')
    qvec = get_embedding(job['jd_text']); results = store.search(qvec, top_k=top_k); out=[]
    for meta, score in results: out.append({'meta': meta, 'score': score})
    return out
if __name__=='__main__': uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=True)
