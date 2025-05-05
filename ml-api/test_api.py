import requests
import json

def test_health():
    response = requests.get('http://localhost:5001/health')
    print("Health check response:", response.json())

def test_prediction():
    test_urls = [
        "http://legitimate-site.com/login",
        "http://suspicious-site.com/verify-account",
        "http://bank-verify.com/secure-login"
    ]
    
    for url in test_urls:
        response = requests.post(
            'http://localhost:5001/predict',
            json={'url': url}
        )
        print(f"\nTesting URL: {url}")
        print("Response:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing ML API...")
    test_health()
    test_prediction() 