import os,pickle,threading,numpy as np
LOCK=threading.Lock()
class SimpleVectorStore:
    def __init__(self,path='vectorstore', dim=384):
        self.path=path; os.makedirs(path, exist_ok=True)
        self.meta_path=os.path.join(path,'meta.pkl'); self.vec_path=os.path.join(path,'vectors.npy')
        self.dim=dim; self.meta=[]; self.vectors=np.zeros((0,dim), dtype=float); self._load()
    def _load(self):
        if os.path.exists(self.meta_path) and os.path.exists(self.vec_path):
            import pickle, numpy as np
            self.meta=pickle.load(open(self.meta_path,'rb'))
            self.vectors=np.load(self.vec_path)
            if self.vectors.ndim==1: self.vectors=self.vectors.reshape(1,-1)
    def add(self, vector, meta):
        v = np.asarray(vector, dtype=float).reshape(1,-1)
        if v.shape[1]!=self.dim: raise ValueError('dim mismatch')
        with LOCK:
            self.meta.append(meta)
            self.vectors = np.vstack([self.vectors, v]) if self.vectors.size else v
            self._persist()
    def search(self, qvec, top_k=5):
        if self.vectors.size==0: return []
        q = np.asarray(qvec, dtype=float)
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)+1e-12
        vecs_n = self.vectors / norms; qn = q/(np.linalg.norm(q)+1e-12)
        sims = vecs_n.dot(qn); idxs = sims.argsort()[::-1][:top_k]
        return [(self.meta[int(i)], float(sims[int(i)])) for i in idxs]
    def _persist(self):
        import pickle, numpy as np
        with open(self.meta_path,'wb') as f: pickle.dump(self.meta, f)
        np.save(self.vec_path, self.vectors)
