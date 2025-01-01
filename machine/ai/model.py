import joblib
from pathlib import Path
from .trainer import extract_features

class PlagiarismModel:
    def __init__(self):
        self.model = None
        self.model_path = Path(__file__).parent / 'model.joblib'
        self.has_model = False
        
        try:
            self.model = joblib.load(self.model_path)
            self.has_model = True
        except:
            print("Warning: AI model not found. Run trainer.py to create one.")
    
    def check_similarity(self, code1, code2):
        if not self.has_model:
            return None
            
        try:
            features = extract_features(code1, code2)
            prediction = self.model.predict([list(features.values())])
            probability = self.model.predict_proba([list(features.values())])
            
            return {
                'is_plagiarism': bool(prediction[0]),
                'confidence': float(max(probability[0]) * 100),
                'features': features
            }
        except Exception as e:
            print(f"AI model error: {e}")
            return None
