import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def extract_url_features(urls):
    """Extract basic features from URLs."""
    features = []
    for url in urls:
        # Basic URL features
        url_len = len(url)
        num_dots = url.count('.')
        num_slashes = url.count('/')
        num_question_marks = url.count('?')
        num_equals = url.count('=')
        num_at = url.count('@')
        num_dashes = url.count('-')
        num_underscores = url.count('_')
        num_tildes = url.count('~')
        num_percent = url.count('%')
        num_ampersand = url.count('&')
        
        features.append([
            url_len, num_dots, num_slashes, num_question_marks,
            num_equals, num_at, num_dashes, num_underscores,
            num_tildes, num_percent, num_ampersand
        ])
    return np.array(features)

def train_phishing_classifier():
    """Train a classifier for phishing URL detection."""
    # For demonstration, we'll use a small synthetic dataset
    # In production, you would load a real dataset
    data = {
        'url': [
            'http://legitimate-site.com/login',
            'http://suspicious-site.com/verify-account',
            'http://bank-verify.com/secure-login',
            'http://paypal-verify.com/account-update',
            'http://amazon-verify.com/order-confirm',
            'http://netflix-verify.com/payment-update',
            'http://apple-verify.com/icloud-update',
            'http://microsoft-verify.com/security-check',
            'http://google-verify.com/account-recovery',
            'http://facebook-verify.com/password-reset'
        ],
        'label': [0, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # 0: legitimate, 1: phishing
    }
    
    df = pd.DataFrame(data)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        df['url'], df['label'], test_size=0.2, random_state=42
    )
    
    # Create a pipeline with TF-IDF vectorizer and Random Forest
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=1000)),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Train the model
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    train_score = pipeline.score(X_train, y_train)
    test_score = pipeline.score(X_test, y_test)
    
    print(f"Training accuracy: {train_score:.3f}")
    print(f"Testing accuracy: {test_score:.3f}")
    
    # Save the model
    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline, 'models/phishing_classifier.joblib')
    print("Model saved to models/phishing_classifier.joblib")

if __name__ == "__main__":
    train_phishing_classifier() 