import pickle
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import DATA_DIR

INDEX_PATH = os.path.join(DATA_DIR, 'vector_index.pkl')

class VectorStore:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
        self.documents = []
        self.ids = []
        self.matrix = None

    def rebuild_from_db(self, knowledge_items):
        self.ids = []
        self.documents = []
        for item in knowledge_items:
            self.ids.append(item.id)
            self.documents.append(f"Q: {item.question}\nA: {item.answer}")
        if self.documents:
            self.matrix = self.vectorizer.fit_transform(self.documents)
        self.save()

    def add(self, doc_id: int, text: str):
        self.ids.append(doc_id)
        self.documents.append(text)
        if self.documents:
            self.matrix = self.vectorizer.fit_transform(self.documents)
        self.save()

    def remove(self, doc_id: int):
        if doc_id in self.ids:
            idx = self.ids.index(doc_id)
            self.ids.pop(idx)
            self.documents.pop(idx)
            if self.documents:
                self.matrix = self.vectorizer.fit_transform(self.documents)
            else:
                self.matrix = None
            self.save()

    def search(self, query: str, top_k: int = 5, threshold: float = 0.05):
        if not self.documents or self.matrix is None:
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        results = []
        for i in np.argsort(scores)[::-1][:top_k]:
            if scores[i] >= threshold:
                results.append({
                    "id": self.ids[i],
                    "document": self.documents[i],
                    "similarity": float(scores[i])
                })
        return results

    def save(self):
        with open(INDEX_PATH, 'wb') as f:
            pickle.dump({
                'ids': self.ids,
                'documents': self.documents,
                'vectorizer': self.vectorizer,
                'matrix': self.matrix
            }, f)

    def load(self):
        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, 'rb') as f:
                data = pickle.load(f)
                self.ids = data['ids']
                self.documents = data['documents']
                self.vectorizer = data['vectorizer']
                self.matrix = data['matrix']

vector_store = VectorStore()
