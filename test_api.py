#!/usr/bin/env python3
"""
Simple test script for the unified ML API
Run this after starting the API server with: python api.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['loaded_models']} models loaded")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Is it running?")
        return False

def test_models():
    """Test the models endpoint"""
    print("\n🔍 Testing /models endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Models endpoint: {data['total_loaded']}/{data['total_available']} models loaded")
            for hazard, info in data['models'].items():
                status = "✅" if info['loaded'] else "❌"
                print(f"  {status} {hazard}: {info['path']}")
            return True
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False

def test_features():
    """Test the features endpoint"""
    print("\n🔍 Testing /features endpoint...")
    hazards = ["oil_spill", "algal_bloom", "coastal_erosion"]
    
    for hazard in hazards:
        try:
            response = requests.get(f"{BASE_URL}/features/{hazard}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {hazard}: {len(data['required_features'])} features required")
            else:
                print(f"❌ {hazard}: {response.status_code}")
        except Exception as e:
            print(f"❌ {hazard}: {e}")

def test_prediction(hazard_type, features):
    """Test a prediction endpoint"""
    print(f"\n🔍 Testing prediction for {hazard_type}...")
    
    payload = {
        "hazard_type": hazard_type,
        "features": features
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction successful:")
            print(f"  Prediction: {data['prediction']}")
            print(f"  Probability: {data.get('probability', 'N/A')}")
            print(f"  Features used: {len(data['features_used'])}")
            return True
        else:
            data = response.json()
            print(f"❌ Prediction failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting API tests...")
    print("=" * 50)
    
    # Test basic endpoints
    if not test_health():
        print("\n❌ Health check failed. Make sure the API server is running:")
        print("   python api.py")
        return
    
    test_models()
    test_features()
    
    # Test predictions with sample data
    print("\n🔍 Testing predictions...")
    
    # Test oil spill prediction
    oil_features = {
        "f_1": 0.5,
        "f_2": 0.3, 
        "f_3": 0.8,
        "f_4": 0.2,
        "f_5": 0.6
    }
    test_prediction("oil_spill", oil_features)
    
    # Test algal bloom prediction
    algal_features = {
        "LATITUDE": 37.7749,
        "LONGITUDE": -122.4194,
        "SALINITY": 35.0,
        "WATER_TEMP": 18.5,
        "WIND_SPEED": 12.0,
        "Month": 8
    }
    test_prediction("algal_bloom", algal_features)
    
    # Test coastal erosion prediction
    erosion_features = {
        "Category_o": 1,
        "Nature_of_": 2,
        "Status": 1,
        "Water_Leve": 3,
        "Scale_Mini": 0.5,
        "SHAPE_Leng": 150.0
    }
    test_prediction("coastal_erosion", erosion_features)
    
    print("\n" + "=" * 50)
    print("✅ API tests completed!")

if __name__ == "__main__":
    main()
