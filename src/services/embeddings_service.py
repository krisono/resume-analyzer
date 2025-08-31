from __future__ import annotations
from typing import List
import numpy as np
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na == 0 or nb == 0: return 0.0
    return float(np.dot(a, b) / (na * nb))

class Embeddings:
    def __init__(self, api_key: str | None):
        self.client = None; self.enabled = False
        if api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=api_key); self.enabled = True
            except Exception:
                self.client = None; self.enabled = False

    def embed(self, texts: List[str]) -> List[List[float]]:
        if self.enabled and self.client:
            try:
                resp = self.client.embeddings.create(model="text-embedding-3-small", input=texts)
                return [d.embedding for d in resp.data]
            except Exception:
                pass
        vecs = []
        for t in texts:
            v = np.zeros(256, dtype=float)
            for tok in (t or "").lower().split():
                v[hash(tok) % 256] += 1.0
            vecs.append(v.tolist())
        return vecs

    def similarity(self, a: str, b: str) -> float:
        v = self.embed([a, b])
        return round(_cosine(np.array(v[0]), np.array(v[1])) * 100.0, 1)