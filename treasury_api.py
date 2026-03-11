import numpy as np
from sklearn.ensemble import IsolationForest

class FraudDetectionAI:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,
            random_state=42
        )
        self.training_data = []
        self.is_trained = False

    def add_training_sample(self, tx):
        sample = [
            tx.get("amount", 0),
            tx.get("frequency", 1),
            tx.get("unique_contacts", 1)
        ]
        self.training_data.append(sample)

    def train(self):
        if len(self.training_data) < 10:
            return False
        
        X = np.array(self.training_data)
        try:
            self.model.fit(X)
            self.is_trained = True
            return True
        except:
            return False

    def predict_fraud(self, tx):
        if not self.is_trained:
            return 0
        
        sample = np.array([[
            tx.get("amount", 0),
            tx.get("frequency", 1),
            tx.get("unique_contacts", 1)
        ]])
        
        try:
            prediction = self.model.predict(sample)[0]
            anomaly_score = self.model.score_samples(sample)[0]
            return {
                "is_fraud": prediction == -1,
                "confidence": float(-anomaly_score) if anomaly_score < 0 else 0,
                "risk_level": "HIGH" if prediction == -1 else "LOW"
            }
        except:
            return {"is_fraud": False, "confidence": 0, "risk_level": "UNKNOWN"}
