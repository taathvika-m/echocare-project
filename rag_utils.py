import numpy as np

def chunk_document(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def get_embedding(client, text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class CarePlanIndex:
    def __init__(self, client, filepath="care_plan.txt"):
        self.client = client
        with open(filepath) as f:
            text = f.read()
        self.chunks = chunk_document(text)
        self.embeddings = [get_embedding(client, c) for c in self.chunks]

    def retrieve(self, question, top_k=2):
        q_emb = get_embedding(self.client, question)
        sims = [cosine_similarity(q_emb, e) for e in self.embeddings]
        top_indices = np.argsort(sims)[-top_k:][::-1]
        return "\n\n".join(self.chunks[i] for i in top_indices)
