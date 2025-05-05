from flask import Flask, request, jsonify
import joblib
import os
from datetime import datetime

app = Flask(__name__)

# Load the model
MODEL_PATH = 'models/phishing_classifier.joblib'
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    else:
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

# Initialize the model when the app starts
with app.app_context():
    load_model()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url']
        prediction = model.predict([url])[0]
        probability = model.predict_proba([url])[0]
        
        return jsonify({
            'url': url,
            'is_phishing': bool(prediction),
            'confidence': float(max(probability)),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print(f"Error starting server: {e}") 