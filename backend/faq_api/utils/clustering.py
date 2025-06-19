#backend/faq_api/utils/clustering.py
import numpy as np
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import re
import string
import umap


class MessageClusterer:
    def __init__(self, min_cluster_size=10):
        self.min_cluster_size = min_cluster_size

    def cluster_embeddings(self, embeddings):
        """
        embeddings: list of dictionaries with keys 'message_id', 'embedding', and optionally 'text'
        """
        if not embeddings:
            print("⚠️ No embeddings provided.")
            return {}, [], np.array([])

        print(f"🧪 Clustering {len(embeddings)} message embeddings...")
        vecs = np.array([e['embedding'] for e in embeddings])

        if vecs.size == 0 or len(vecs.shape) != 2:
            raise ValueError("Empty or invalid embeddings provided for clustering.")

        ids = [e['message_id'] for e in embeddings]

        clusterer = hdbscan.HDBSCAN(min_cluster_size=self.min_cluster_size, metric='euclidean')
        labels = clusterer.fit_predict(vecs)

        print(f"📊 Label distribution: {Counter(labels)}")

        clustered = {}
        id_to_label = {}

        for i, label in enumerate(labels):
            id_to_label[ids[i]] = label
            if label == -1:
                continue  # noise
            clustered.setdefault(label, []).append({
                "message_id": ids[i],
                "embedding": embeddings[i]['embedding'],
                "text": embeddings[i].get('text', ''),
                "created_at": embeddings[i].get('created_at')  # for pipeline summary
            })

        print(f"✅ Clusters formed: {len(clustered)} (Noise points: {sum(l == -1 for l in labels)})")
        return clustered, labels, vecs

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
        if not faqs or not centroids:
            raise ValueError("Cannot match FAQs — missing input.")

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

    def extract_keywords(self, texts, top_n=10):
        words = []
        for text in texts:
            text = text.lower()
            text = re.sub(rf"[{string.punctuation}]", "", text)
            words.extend(text.split())

        stopwords = set([
            "the", "a", "an", "and", "or", "in", "on", "is", "to", "of",
            "for", "with", "i", "we", "you", "it", "this", "that", "at",
            "by", "be", "was", "are", "as", "from"
        ])
        filtered = [w for w in words if w not in stopwords and len(w) > 2]
        return [word for word, _ in Counter(filtered).most_common(top_n)]

    def get_cluster_map_coords(self, embeddings, labels, vecs=None):
        if not embeddings:
            print("⚠️ No embeddings for UMAP projection.")
            return []

        if vecs is None:
            vecs = np.array([e['embedding'] for e in embeddings])

        if vecs.size == 0:
            print("⚠️ Empty vectors for UMAP projection.")
            return []

        try:
            reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='cosine')
            reduced = reducer.fit_transform(vecs)
        except Exception as e:
            print(f"❌ UMAP reduction failed: {e}")
            return []

        return [
            {
                "id": e["message_id"],
                "x": float(pos[0]),
                "y": float(pos[1]),
                "label": int(label)
            }
            for e, pos, label in zip(embeddings, reduced, labels)
            if label != -1
        ]
