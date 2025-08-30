#!/usr/bin/env python3
"""
Complete demo script for the Coastal Hazard Detection System
This demonstrates the full pipeline from training to prediction to alerts
"""

import os
import json
import time
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print("-" * 40)

def check_files():
    """Check if required files exist"""
    print_section("Checking Required Files")
    
    required_files = [
        "data/oil_spill.csv",
        "data/algal_bloom.csv", 
        "data/shoreline.csv"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            return False
    
    return True

def check_models():
    """Check if trained models exist"""
    print_section("Checking Trained Models")
    
    model_files = [
        "models/oil_spill_rf.pkl",
        "models/algal_bloom_rf.pkl",
        "models/coastal_erosion_rf.pkl"
    ]
    
    models_exist = True
    for model_path in model_files:
        if os.path.exists(model_path):
            print(f"✅ {model_path}")
        else:
            print(f"❌ {model_path} - Not trained yet")
            models_exist = False
    
    return models_exist

def check_artifacts():
    """Check if training artifacts exist"""
    print_section("Checking Training Artifacts")
    
    artifact_dirs = [
        "artifacts/oil_spill",
        "artifacts/algal_blooms", 
        "artifacts/coastal_erosion"
    ]
    
    for artifact_dir in artifact_dirs:
        if os.path.exists(artifact_dir):
            files = os.listdir(artifact_dir)
            print(f"✅ {artifact_dir} ({len(files)} files)")
            for file in files:
                print(f"   📄 {file}")
        else:
            print(f"❌ {artifact_dir} - Not created yet")

def show_sample_metrics():
    """Show sample metrics from training"""
    print_section("Sample Training Metrics")
    
    metrics_files = [
        "artifacts/oil_spill/metrics.json",
        "artifacts/algal_blooms/metrics.json",
        "artifacts/coastal_erosion/metrics.json"
    ]
    
    for metrics_file in metrics_files:
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                
                # Extract key metrics
                if 'accuracy' in metrics:
                    print(f"📊 {os.path.dirname(metrics_file).split('/')[-1]}:")
                    print(f"   Accuracy: {metrics['accuracy']:.3f}")
                    print(f"   Precision: {metrics['precision']:.3f}")
                    print(f"   Recall: {metrics['recall']:.3f}")
                    print(f"   F1-Score: {metrics['f1_score']:.3f}")
                elif 'r2_score' in metrics:
                    print(f"📊 {os.path.dirname(metrics_file).split('/')[-1]}:")
                    print(f"   R² Score: {metrics['r2_score']:.3f}")
                    print(f"   MSE: {metrics['mse']:.3f}")
            except Exception as e:
                print(f"❌ Error reading {metrics_file}: {e}")

def demo_prediction_pipeline():
    """Demonstrate the prediction pipeline"""
    print_section("ML Prediction Pipeline Demo")
    
    print("🎯 This demonstrates how the system would make predictions:")
    print("\n1. User uploads image with GPS coordinates")
    print("2. System extracts features from image and location")
    print("3. ML models predict hazard probability")
    print("4. System determines alert level")
    print("5. Multi-channel alerts are sent")
    
    print("\n📱 Sample Citizen Report:")
    print("   📍 Location: San Francisco Bay (37.7749, -122.4194)")
    print("   📸 Image: thermal_camera_detection.mp4")
    print("   📝 Description: 'Possible oil slick detected'")
    print("   📞 Phone: +1-555-123-4567")
    
    print("\n🤖 ML Model Prediction:")
    print("   🚨 Hazard Type: Oil Spill")
    print("   📊 Confidence: 87%")
    print("   🚦 Alert Level: ORANGE")
    
    print("\n📢 Alert Channels:")
    print("   📧 Email: Sent to emergency contacts")
    print("   📱 SMS: Sent to key personnel")
    print("   📞 IVR: Voice call to supervisor")
    print("   🔗 Webhook: Integration with emergency systems")

def demo_alert_system():
    """Demonstrate the alert system"""
    print_section("Multi-Channel Alert System Demo")
    
    print("🚨 Alert System Capabilities:")
    print("\n📧 Email Alerts:")
    print("   • HTML formatted with images")
    print("   • Priority levels: ORANGE, RED")
    print("   • Configurable SMTP settings")
    
    print("\n📱 SMS Alerts (Twilio):")
    print("   • Priority levels: RED only")
    print("   • Custom message templates")
    print("   • Multiple recipient support")
    
    print("\n📞 IVR Voice Calls:")
    print("   • Priority levels: RED only")
    print("   • Automated voice announcements")
    print("   • Call recording and logging")
    
    print("\n🔗 Webhook Integration:")
    print("   • HTTP endpoints for external systems")
    print("   • JSON payload with hazard details")
    print("   • Configurable authentication")

def show_api_endpoints():
    """Show available API endpoints"""
    print_section("Unified ML API Endpoints")
    
    print("🌐 API Server: http://localhost:8000")
    print("\n📡 Available Endpoints:")
    print("   GET  /health           - System health and model status")
    print("   GET  /models           - List all available models")
    print("   GET  /features/{type} - Get required features for hazard type")
    print("   POST /predict          - Make ML predictions")
    
    print("\n🔧 Start the API:")
    print("   python api.py")
    print("   # or")
    print("   make api")
    
    print("\n🧪 Test the API:")
    print("   python test_api.py")
    print("   # or")
    print("   make test-api")

def show_tide_monitoring():
    """Show tide monitoring capabilities"""
    print_section("Tide Monitoring Service")
    
    print("🌊 Tide Monitoring Features:")
    print("   • Real-time tide level monitoring")
    print("   • Historical tide data analysis")
    print("   • Tide prediction algorithms")
    print("   • Integration with hazard detection")
    
    print("\n🔧 Start Tide Service:")
    print("   python tide_api.py")
    print("   # or")
    print("   make tide-api")
    
    print("\n🌐 Web Interface: http://localhost:5000")

def show_quick_commands():
    """Show quick commands for judges"""
    print_section("Quick Commands for Judges")
    
    print("⚡ Fast Setup:")
    print("   make install          # Install dependencies")
    print("   make train            # Train all models")
    print("   make api              # Start ML API")
    print("   make tide-api         # Start tide monitoring")
    
    print("\n🧪 Testing:")
    print("   make test             # Run integration tests")
    print("   make test-api         # Test ML API")
    print("   python demo.py        # Run this demo")
    
    print("\n📊 View Results:")
    print("   ls -la artifacts/*/   # Show training results")
    print("   cat artifacts/*/metrics.json  # View metrics")
    print("   ls -la models/        # Show trained models")

def main():
    """Main demo function"""
    print_header("Coastal Hazard Detection System - Complete Demo")
    
    print("🎯 This demo shows the complete pipeline from data to alerts")
    print("📅 Demo Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Check system status
    if not check_files():
        print("\n❌ Missing required data files. Please ensure data/ directory contains:")
        print("   • oil_spill.csv")
        print("   • algal_bloom.csv") 
        print("   • shoreline.csv")
        return
    
    check_models()
    check_artifacts()
    show_sample_metrics()
    
    # Show capabilities
    demo_prediction_pipeline()
    demo_alert_system()
    show_api_endpoints()
    show_tide_monitoring()
    
    # Quick commands
    show_quick_commands()
    
    print_header("Demo Complete!")
    print("🚀 Your system is ready for judges!")
    print("\n💡 Next steps:")
    print("   1. Train models: make train")
    print("   2. Start API: make api")
    print("   3. Test predictions: make test-api")
    print("   4. Show tide monitoring: make tide-api")

if __name__ == "__main__":
    main()
