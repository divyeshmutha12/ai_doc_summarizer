import faiss
from openai import OpenAI
import os
import pickle
from dotenv import load_dotenv
from ..core.utils import chunk_text
import numpy as np

load_dotenv()

class EmbeddingModel:
    def __init__(self, index_path="faiss_index/index.faiss", meta_path="faiss_index/meta.pkl"):
        self.index_path = index_path
        self.meta_path = meta_path
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.dim = 1536  # text-embedding-3-small
        self.index = None
        self.documents = []
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.documents = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            self.documents = []

    def _save_index(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.documents, f)

    def get_embedding(self, text):
        resp = self.client.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding

    def add_documents(self, texts, metadata=None):
        chunks = []
        for t in texts:
            if isinstance(t, str):
                chunks.append(t)
            elif isinstance(t, dict) and "text" in t:
                chunks.append(t["text"])
        embeddings = [self.get_embedding(chunk) for chunk in chunks]
        self.index.add(np.array(embeddings).astype("float32"))
        for i, chunk in enumerate(chunks):
            self.documents.append({"text": chunk, "metadata": metadata})
        self._save_index()

    def search(self, query, top_k=5):
        if len(self.documents) == 0:
            return []

        q_emb = np.array([self.get_embedding(query)]).astype("float32")
        # Limit top_k to the number of documents available
        actual_k = min(top_k, len(self.documents))
        D, I = self.index.search(q_emb, actual_k)
        results = []
        for idx in I[0]:
            if idx >= 0 and idx < len(self.documents):
                results.append(self.documents[idx])
        return results

    def get_all_documents(self):
        return self.documents
