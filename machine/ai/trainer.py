import json
import pandas as pd
from pathlib import Path
import difflib
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def load_training_data(training_dir):
    """Load known plagiarism cases for training"""
    training_path = Path(training_dir)
    data = []
    
    # Load all training pairs from training directory
    for json_file in training_path.glob('*.json'):
        with open(json_file, 'r') as f:
            training_case = json.load(f)
            data.append({
                'code1': training_case['code1'],
                'code2': training_case['code2'],
                'is_plagiarism': training_case['is_plagiarism'],
                'similarity_score': training_case['similarity_score']
            })
    
    return data

def extract_features(code1, code2):
    """Extract features from code pairs"""
    features = {}
    
    # Line similarity
    matcher = difflib.SequenceMatcher(None, code1, code2)
    features['text_similarity'] = matcher.ratio()
    
    # Structure similarity (indentation patterns)
    indent1 = [len(line) - len(line.lstrip()) for line in code1.splitlines()]
    indent2 = [len(line) - len(line.lstrip()) for line in code2.splitlines()]
    features['structure_similarity'] = difflib.SequenceMatcher(None, str(indent1), str(indent2)).ratio()
    
    # Variable name similarity
    var_pattern = re.compile(r'\b[a-zA-Z_]\w*\b')
    vars1 = set(var_pattern.findall(code1))
    vars2 = set(var_pattern.findall(code2))
    features['var_name_similarity'] = len(vars1.intersection(vars2)) / max(len(vars1), len(vars2)) if vars1 or vars2 else 0
    
    return features

def train_model(training_data):
    """Train the plagiarism detection model"""
    features = []
    labels = []
    
    for case in training_data:
        case_features = extract_features(case['code1'], case['code2'])
        features.append(list(case_features.values()))
        labels.append(case['is_plagiarism'])
    
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2)
    
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy * 100:.2f}%")
    
    return model

def save_model(model, path='model.joblib'):
    """Save the trained model"""
    joblib.dump(model, path)
    print(f"Model saved to {path}")

def main():
    # Training directory should contain JSON files with code pairs and labels
    training_dir = Path(__file__).parent.parent / 'data' / 'training'
    training_dir.mkdir(exist_ok=True)
    
    # Load training data
    print("Loading training data...")
    training_data = load_training_data(training_dir)
    
    if not training_data:
        print("No training data found. Please add training cases to data/training/")
        return
    
    # Train model
    print("Training model...")
    model = train_model(training_data)
    
    # Save model
    save_model(model)

if __name__ == '__main__':
    main()
