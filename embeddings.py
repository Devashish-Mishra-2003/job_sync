import numpy as np
MODEL=None; EMB_DIM=384
try:
    from sentence_transformers import SentenceTransformer
    MODEL = SentenceTransformer('all-MiniLM-L6-v2'); EMB_DIM=MODEL.get_sentence_embedding_dimension()
except Exception:
    MODEL=None
def get_embedding(text):
    if MODEL: return MODEL.encode(text, convert_to_numpy=True).astype(float)
    import numpy as np, hashlib
    h = int(hashlib.sha256(text.encode('utf-8')).hexdigest(),16) % (10**8)
    rng = np.random.RandomState(h); return rng.rand(EMB_DIM).astype(float)
def cosine_similarity(a,b):
    a=a/(np.linalg.norm(a)+1e-12); b=b/(np.linalg.norm(b)+1e-12); return float(a.dot(b))
