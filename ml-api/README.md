# ML API - Phishing URL Detection Service

A Flask-based microservice that provides real-time phishing URL detection using machine learning. The service uses a Random Forest classifier trained on URL features to identify potentially malicious URLs.

## Features

- Real-time URL classification
- Confidence scores for predictions
- Health check endpoint
- Easy-to-use REST API
- Model persistence and loading
- Comprehensive error handling
- Development mode with debugging

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository and navigate to the ml-api directory:
```bash
cd ml-api
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Train the initial model:
```bash
python train_model.py
```

## Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:5001` (port 5001 is used to avoid conflicts with macOS AirPlay).

### API Endpoints

#### Health Check
```bash
GET /health
```
Response:
```json
{
    "status": "healthy",
    "model_loaded": true,
    "timestamp": "2024-03-14T12:00:00Z"
}
```

#### URL Prediction
```bash
POST /predict
Content-Type: application/json

{
    "url": "http://example.com"
}
```
Response:
```json
{
    "url": "http://example.com",
    "is_phishing": false,
    "confidence": 0.95,
    "timestamp": "2024-03-14T12:00:00Z"
}
```

### Testing

Run the test script to verify the API functionality:
```bash
python test_api.py
```

## Model Details

The phishing URL classifier uses a two-stage pipeline:

1. **Feature Extraction**:
   - URL length
   - Number of dots (.)
   - Number of slashes (/)
   - Number of question marks (?)
   - Number of equals (=)
   - Number of @ symbols
   - Number of dashes (-)
   - Number of underscores (_)
   - Number of tildes (~)
   - Number of percent signs (%)
   - Number of ampersands (&)
   - TF-IDF features from URL text

2. **Classification**:
   - Random Forest with 100 trees
   - Binary classification (phishing/legitimate)
   - Probability scores for confidence

## Project Structure

```
ml-api/
├── app.py           # Flask API server
├── train_model.py   # Model training script
├── test_api.py      # API testing script
├── requirements.txt # Dependencies
├── .gitignore      # Git ignore file
├── setup.sh        # Setup script
└── models/         # Directory for saved models
    └── phishing_classifier.joblib
```

## Development

### Adding New Features

1. Update the feature extraction in `train_model.py`
2. Retrain the model
3. Update the API endpoints in `app.py` if needed

### Testing New Features

1. Add test cases to `test_api.py`
2. Run the test script to verify changes

## Error Handling

The API handles various error cases:
- Missing model file
- Invalid JSON input
- Missing URL parameter
- Model prediction errors
- Server errors

## Future Improvements

- [ ] Use real-world phishing URL dataset
- [ ] Add more sophisticated features:
  - Domain age
  - SSL certificate information
  - Domain reputation
  - Character distribution
  - URL entropy
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Add model versioning
- [ ] Add monitoring and logging
- [ ] Add HTTPS support
- [ ] Implement model retraining pipeline
- [ ] Add Docker containerization
- [ ] Add load balancing for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- scikit-learn for the machine learning pipeline
- Flask for the web framework
- The open-source community for various tools and libraries 