import re
from typing import Dict, Any, Tuple

# Try importing scikit-learn, otherwise implement high-fidelity fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Class vocabulary categories for rule-based matching and TF-IDF training fallback
CATEGORIES = {
    "FIR PDF": ["fir", "first information report", "police station", "under section", "complainant", "ipc", "crpc", "accused"],
    "Witness Statement": ["statement of", "witness", "testified", "witnessed", "saw him", "heard a noise", "swore under oath", "testimony"],
    "Call Record": ["cdr", "call data record", "cell tower", "calling party", "receiving party", "duration", "imei", "imsi", "ping"],
    "Vehicle Details": ["registration", "license plate", "rc book", "vehicle", "chassis", "car model", "color", "registration number", "chassis number"],
    "Suspect History": ["criminal record", "prior arrest", "conviction", "alias", "modus operandi", "previous arrest", "gang association", "convicted"],
    "Location Coordinates": ["coordinates", "latitude", "longitude", "gps", "location marker", "degree", "map location", "geofence"],
}

class EvidenceClassifier:
    def __init__(self):
        self.categories = list(CATEGORIES.keys())
        if HAS_SKLEARN:
            self._train_ml_model()

    def _train_ml_model(self):
        """Train a lightweight Naive Bayes model on synthetic police texts."""
        texts = []
        labels = []
        for cat, keywords in CATEGORIES.items():
            for kw in keywords:
                # Add multiple synthetic sentences containing the keyword to train the vectorizer
                texts.append(f"The document belongs to the case files. It contains details regarding {kw}.")
                texts.append(f"Official evidence logs: {kw} details recorded on scene.")
                labels.append(cat)
                
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        self.model = MultinomialNB()
        
        # Fit model
        x_train = self.vectorizer.fit_transform(texts)
        self.model.fit(x_train, labels)

    def classify_by_extension(self, filename: str) -> str:
        """Classify purely based on file extension."""
        ext = filename.split(".")[-1].lower()
        if ext in ["jpg", "jpeg", "png", "bmp"]:
            return "Image"
        elif ext in ["mp4", "avi", "mkv", "mov"]:
            return "CCTV"
        elif ext in ["mp3", "wav", "m4a", "ogg"]:
            return "Audio"
        elif ext == "pdf":
            return "FIR PDF"
        return "Unknown"

    def classify_text_content(self, text: str) -> Tuple[str, float]:
        """Classify text file contents using Machine Learning or rule-based fallback."""
        if not text:
            return "Unknown", 0.0
            
        text_lower = text.lower()
        
        if HAS_SKLEARN:
            try:
                x_test = self.vectorizer.transform([text_lower])
                probs = self.model.predict_proba(x_test)[0]
                max_idx = probs.argmax()
                predicted_cat = self.model.classes_[max_idx]
                confidence = probs[max_idx]
                # If confidence is extremely low, fall back to rule-based keyword match
                if confidence > 0.35:
                    return predicted_cat, float(confidence)
            except Exception:
                pass
                
        # Rule-based fallback (Keyword Frequency Analyzer)
        scores = {}
        for category, keywords in CATEGORIES.items():
            score = 0
            for kw in keywords:
                score += len(re.findall(re.escape(kw), text_lower))
            scores[category] = score
            
        best_cat = max(scores, key=scores.get)
        if scores[best_cat] > 0:
            total = sum(scores.values())
            confidence = scores[best_cat] / total
            return best_cat, round(confidence, 2)
            
        return "Document", 0.50

    def predict(self, filename: str, content_text: str = "") -> Tuple[str, float]:
        """Expose main classification interface combining filename and content."""
        ext_class = self.classify_by_extension(filename)
        if ext_class != "Unknown" and ext_class != "FIR PDF":
            return ext_class, 0.95
            
        if content_text:
            return self.classify_text_content(content_text)
            
        return ext_class if ext_class != "Unknown" else ("Document", 0.50)

# Initialize global classifier instance
classifier = EvidenceClassifier()

def get_evidence_classifier():
    return classifier
