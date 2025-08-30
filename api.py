# api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os
import json
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)

MODEL_PATHS = {
    "oil_spill": "models/oil_spill_rf.pkl",
    "algal_bloom": "models/algal_bloom_rf.pkl",
    "coastal_erosion": "models/coastal_erosion_rf.pkl"
}
MODELS = {}

FEATURES = {
    "oil_spill": ["f_1", "f_2", "f_3", "f_4", "f_5"],  # adjust to your CSV features
    "algal_bloom": ["LATITUDE", "LONGITUDE", "SALINITY", "WATER_TEMP", "WIND_SPEED", "Month"],
    "coastal_erosion": ["Category_o", "Nature_of_", "Status", "Water_Leve", "Scale_Mini", "SHAPE_Leng"]
}

def load_models():
    """Load all trained models on startup"""
    for k, p in MODEL_PATHS.items():
        if os.path.exists(p):
            try:
                MODELS[k] = joblib.load(p)
                print(f"✅ Loaded {k} model from {p}")
            except Exception as e:
                print(f"❌ Failed to load {k} model: {e}")
        else:
            print(f"⚠️ Model not found: {p}")

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "ok": True, 
        "loaded_models": list(MODELS.keys()),
        "available_hazards": list(MODEL_PATHS.keys()),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/predict", methods=["POST"])
def predict():
    """Main prediction endpoint"""
    try:
        data = request.get_json(force=True)
        hazard = data.get("hazard_type")
        payload = data.get("features", {})
        
        if not hazard:
            return jsonify({"error": "hazard_type is required"}), 400
            
        if hazard not in MODELS:
            return jsonify({
                "error": f"model not loaded for {hazard}",
                "available_models": list(MODELS.keys())
            }), 400
            
        if hazard not in FEATURES:
            return jsonify({"error": f"unknown hazard type: {hazard}"}), 400
            
        feats = FEATURES[hazard]
        
        # Validate all required features are present
        missing_features = [f for f in feats if f not in payload]
        if missing_features:
            return jsonify({
                "error": f"missing features: {missing_features}",
                "required": feats,
                "received": list(payload.keys())
            }), 400

        # Convert features to numpy array
        try:
            x = np.array([[payload[f] for f in feats]], dtype=float)
        except (ValueError, TypeError) as e:
            return jsonify({
                "error": f"invalid feature values: {str(e)}",
                "required": feats,
                "example": {f: "numeric_value" for f in feats}
            }), 400

        model = MODELS[hazard]
        
        # Get prediction
        pred = int(model.predict(x)[0])
        
        # Get probability if available
        proba = None
        if hasattr(model, "predict_proba"):
            try:
                proba = float(model.predict_proba(x)[0, 1])
            except:
                pass

        return jsonify({
            "hazard_type": hazard,
            "prediction": pred,
            "probability": proba,
            "features_used": feats,
            "timestamp": datetime.now().isoformat(),
            "model_info": {
                "type": type(model).__name__,
                "features_count": len(feats)
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": f"prediction failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/models", methods=["GET"])
def list_models():
    """List available models and their status"""
    model_info = {}
    for hazard, path in MODEL_PATHS.items():
        model_info[hazard] = {
            "loaded": hazard in MODELS,
            "path": path,
            "exists": os.path.exists(path),
            "features": FEATURES.get(hazard, [])
        }
    
    return jsonify({
        "models": model_info,
        "total_loaded": len(MODELS),
        "total_available": len(MODEL_PATHS)
    })

@app.route("/features/<hazard_type>", methods=["GET"])
def get_features(hazard_type):
    """Get required features for a specific hazard type"""
    if hazard_type not in FEATURES:
        return jsonify({"error": f"unknown hazard type: {hazard_type}"}), 400
        
    return jsonify({
        "hazard_type": hazard_type,
        "required_features": FEATURES[hazard_type],
        "example_request": {
            "hazard_type": hazard_type,
            "features": {f: "numeric_value" for f in FEATURES[hazard_type]}
        }
    })

if __name__ == "__main__":
    print("🚀 Loading ML models...")
    load_models()
    print(f"📊 Loaded {len(MODELS)} models")
    print("🌐 Starting API server on http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
