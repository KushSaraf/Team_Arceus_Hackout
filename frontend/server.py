#!/usr/bin/env python3
"""
Frontend Development Server for CoastalGuard AI

A simple Flask server to serve the frontend files during development and hackathon demos.
"""

from flask import Flask, send_from_directory, render_template_string
import os
import json
from datetime import datetime

app = Flask(__name__)

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Mock API endpoints for frontend testing
@app.route('/api/health')
def health():
    return json.dumps({
        "ok": True,
        "loaded_models": ["oil_spill", "algal_bloom", "coastal_erosion"],
        "available_hazards": ["oil_spill", "algal_bloom", "coastal_erosion"],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/predict', methods=['POST'])
def mock_predict():
    """Mock prediction endpoint for frontend testing"""
    import random
    
    # Simulate different hazard types and predictions
    hazard_types = ['oil_spill', 'algal_bloom', 'coastal_erosion']
    hazard_type = random.choice(hazard_types)
    
    # Simulate prediction results
    prediction = random.choice([0, 1, 2, 3])  # 0 = no hazard, 1-3 = different alert levels
    probability = random.uniform(0.6, 0.95)
    
    return json.dumps({
        "hazard_type": hazard_type,
        "prediction": prediction,
        "probability": probability,
        "features_used": ["feature1", "feature2", "feature3"],
        "timestamp": datetime.now().isoformat(),
        "model_info": {
            "type": "RandomForestClassifier",
            "features_count": 6
        }
    })

@app.route('/api/upload', methods=['POST'])
def mock_upload():
    """Mock image upload endpoint for frontend testing"""
    import random
    
    # Simulate image analysis
    prediction = random.choice([0, 1, 2, 3])
    probability = random.uniform(0.7, 0.95)
    
    return json.dumps({
        "hazard_type": "oil_spill",
        "prediction": prediction,
        "probability": probability,
        "features_used": ["image_features"],
        "timestamp": datetime.now().isoformat(),
        "model_info": {
            "type": "ImageClassifier",
            "features_count": 1
        }
    })

@app.route('/api/tide/status')
def mock_tide_status():
    """Mock tide status endpoint"""
    import random
    
    return json.dumps({
        "current_level": round(random.uniform(0.5, 2.5), 1),
        "tide_phase": random.choice(["Rising", "Falling", "High", "Low"]),
        "location_name": "San Francisco Bay",
        "forecast": [
            {"time": "00:00", "level": 1.2},
            {"time": "06:00", "level": 2.1},
            {"time": "12:00", "level": 0.8},
            {"time": "18:00", "level": 1.9},
            {"time": "23:00", "level": 1.3}
        ]
    })

if __name__ == '__main__':
    print("🌐 Starting CoastalGuard AI Frontend Server...")
    print("📱 Frontend will be available at: http://localhost:3000")
    print("🔧 Mock API endpoints available at: http://localhost:3000/api/*")
    print("🚀 Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=3000, debug=True)
