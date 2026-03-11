import numpy as np
import networkx as nx
from sklearn.cluster import DBSCAN

class WalletClusterAI:
    def __init__(self):
        self.graph = nx.Graph()
        self.clusters = {}

    def add_transaction(self, tx):
        sender = tx.get("from", "")
        receiver = tx.get("to", "")
        if sender and receiver:
            self.graph.add_edge(sender, receiver)

    def cluster_wallets(self):
        nodes = list(self.graph.nodes())
        
        if len(nodes) < 3:
            return {}

        index_map = {n: i for i, n in enumerate(nodes)}
        edges = [(index_map[a], index_map[b]) for a, b in self.graph.edges()]

        if not edges:
            return {0: nodes}

        data = np.array(edges)
        model = DBSCAN(eps=1.5, min_samples=2)
        labels = model.fit_predict(data)

        clusters = {}
        for idx, label in enumerate(labels):
            wallet_a = nodes[data[idx][0]]
            wallet_b = nodes[data[idx][1]]
            if label not in clusters:
                clusters[label] = set()
            clusters[label].add(wallet_a)
            clusters[label].add(wallet_b)

        self.clusters = {k: list(v) for k, v in clusters.items()}
        return self.clusters

    def get_cluster_risk(self, cluster_id):
        if cluster_id not in self.clusters:
            return 0
        return len(self.clusters[cluster_id]) * 0.5

    def detect_anomalies(self):
        self.cluster_wallets()
        anomalies = []
        for cluster_id, wallets in self.clusters.items():
            if len(wallets) > 5:
                anomalies.append({
                    "cluster_id": cluster_id,
                    "wallet_count": len(wallets),
                    "risk_level": "MEDIUM" if len(wallets) < 10 else "HIGH"
                })
        return anomalies
