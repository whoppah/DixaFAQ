import numpy as np
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity

class MessageClusterer:
    def __init__(self, min_cluster_size=10):
        self.min_cluster_size = min_cluster_size

    def cluster_embeddings(self, embeddings):
        """
        embeddings: list of dictionaries with keys 'id', 'embedding', and optionally 'text'
        """
        vecs = np.array([e['embedding'] for e in embeddings])
        ids = [e['id'] for e in embeddings]

        clusterer = hdbscan.HDBSCAN(min_cluster_size=self.min_cluster_size, metric='euclidean')
        labels = clusterer.fit_predict(vecs)

        clustered = {}
        for i, label in enumerate(labels):
            if label == -1:
                continue  # noise
            clustered.setdefault(label, []).append({
                "id": ids[i],
                "embedding": embeddings[i]['embedding'],
                "text": embeddings[i].get('text', '')
            })

        return clustered

    def compute_centroids(self, clusters):
        centroids = {}
        for label, items in clusters.items():
            vecs = np.array([item['embedding'] for item in items])
            centroid = vecs.mean(axis=0)
            centroids[label] = centroid
        return centroids

    def match_faqs(self, centroids, faqs):
        """
        faqs: list of dicts with 'question', 'embedding'
        """
        faq_vectors = np.array([f['embedding'] for f in faqs])
        cluster_ids = list(centroids.keys())
        centroid_vecs = np.array([centroids[cid] for cid in cluster_ids])

        similarities = cosine_similarity(centroid_vecs, faq_vectors)
        results = {}

        for i, cid in enumerate(cluster_ids):
            top_faq_index = np.argmax(similarities[i])
            results[cid] = {
                "matched_faq": faqs[top_faq_index]['question'],
                "similarity": similarities[i][top_faq_index]
            }

        return results
