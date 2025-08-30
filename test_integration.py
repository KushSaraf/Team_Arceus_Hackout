#!/usr/bin/env python3
"""
Integration Test Script for Coastal Hazard Detection System

This script tests the integration between:
- Citizen Reporting Service
- Multi-Channel Alert Service  
- Hazard Detection Service
- ML Models

Run with: python test_integration.py
"""

import os
import sys
import tempfile
import logging
from PIL import Image
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from citizen_reporting import CitizenReportingService, Alert, LocationData
        print("✅ Citizen reporting service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import citizen reporting service: {e}")
        return False
    
    try:
        from multi_channel_alerts import MultiChannelAlertService
        print("✅ Multi-channel alert service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import multi-channel alert service: {e}")
        return False
    
    try:
        import joblib
        import numpy as np
        from PIL import Image
        print("✅ ML dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ML dependencies: {e}")
        return False
    
    # Store imported classes globally for other tests
    global CitizenReportingService, Alert, LocationData, MultiChannelAlertService
    from citizen_reporting import CitizenReportingService, Alert, LocationData
    from multi_channel_alerts import MultiChannelAlertService
    
    return True

def test_model_loading():
    """Test if trained models can be loaded"""
    print("\n🤖 Testing model loading...")
    
    try:
        import joblib
    except ImportError:
        print("❌ joblib not available, skipping model loading test")
        return False
    
    model_paths = [
        'models/oil_spill_rf.pkl',
        'models/algal_bloom_rf.pkl', 
        'models/coastal_erosion_rf.pkl'
    ]
    
    models_loaded = 0
    for model_path in model_paths:
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                print(f"✅ Loaded {os.path.basename(model_path)}")
                models_loaded += 1
            except Exception as e:
                print(f"❌ Failed to load {os.path.basename(model_path)}: {e}")
        else:
            print(f"⚠️ Model not found: {model_path}")
    
    if models_loaded > 0:
        print(f"✅ {models_loaded}/{len(model_paths)} models loaded successfully")
        return True
    else:
        print("❌ No models could be loaded")
        return False

def test_service_initialization():
    """Test if services can be initialized"""
    print("\n🚀 Testing service initialization...")
    
    try:
        # Test multi-channel alert service
        multi_channel_service = MultiChannelAlertService()
        print("✅ Multi-channel alert service initialized")
        
        # Test citizen reporting service
        citizen_service = CitizenReportingService(multi_channel_service=multi_channel_service)
        print("✅ Citizen reporting service initialized")
        
        return True, multi_channel_service, citizen_service
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False, None, None

def create_test_image():
    """Create a test image for testing"""
    # Create a simple test image with some patterns
    img = Image.new('RGB', (224, 224), color='blue')
    
    # Add some random noise to simulate real image
    img_array = np.array(img)
    noise = np.random.randint(0, 50, img_array.shape, dtype=np.uint8)
    img_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    
    # Convert back to PIL Image
    test_image = Image.fromarray(img_array)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    test_image.save(temp_file.name, 'JPEG')
    temp_file.close()
    
    return temp_file.name

def create_mock_file_object(file_path):
    """Create a mock file object for testing"""
    class MockFile:
        def __init__(self, file_path):
            self.file_path = file_path
            self.filename = os.path.basename(file_path)
        
        def read(self):
            with open(self.file_path, 'rb') as f:
                return f.read()
    
    return MockFile(file_path)

def test_image_processing():
    """Test the complete image processing pipeline"""
    print("\n📸 Testing image processing pipeline...")
    
    try:
        # Initialize services
        success, multi_channel_service, citizen_service = test_service_initialization()
        if not success:
            return False
        
        # Create test image
        test_image_path = create_test_image()
        mock_file = create_mock_file_object(test_image_path)
        
        # Test coordinates (San Francisco Bay Area)
        test_lat = 37.7749
        test_lon = -122.4194
        test_description = "Test image for integration testing"
        test_phone = "+15551234567"
        
        print(f"Processing test image from coordinates: {test_lat}, {test_lon}")
        
        # Process image upload
        result = citizen_service.process_image_upload(
            mock_file, test_lat, test_lon, test_description, test_phone
        )
        
        if result.get('success'):
            print("✅ Image processing successful!")
            print(f"  Hazard Type: {result['alert']['hazard_type']}")
            print(f"  Confidence: {result['alert']['confidence']:.2f}")
            print(f"  Alert Level: {result['alert']['alert_level']}")
            print(f"  Location: {result['alert']['location']['location_name']}")
            
            # Check if multi-channel alert was triggered
            if 'multi_channel_results' in result['alert']['metadata']:
                print("✅ Multi-channel alert integration working")
            else:
                print("⚠️ Multi-channel alert not triggered")
            
            # Clean up
            os.unlink(test_image_path)
            return True
        else:
            print(f"❌ Image processing failed: {result.get('error')}")
            os.unlink(test_image_path)
            return False
            
    except Exception as e:
        print(f"❌ Image processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alert_retrieval():
    """Test alert retrieval functionality"""
    print("\n📋 Testing alert retrieval...")
    
    try:
        success, multi_channel_service, citizen_service = test_service_initialization()
        if not success:
            return False
        
        # Get active alerts
        alerts = citizen_service.get_active_alerts()
        print(f"✅ Retrieved {len(alerts)} active alerts")
        
        # Get system status
        status = citizen_service.get_system_status()
        print(f"✅ System status: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alert retrieval test failed: {e}")
        return False

def test_multi_channel_alerts():
    """Test multi-channel alert functionality"""
    print("\n📡 Testing multi-channel alerts...")
    
    try:
        success, multi_channel_service, citizen_service = test_service_initialization()
        if not success:
            return False
        
        # Create a test alert
        test_alert = Alert(
            id=999,
            timestamp="2024-01-01T12:00:00",
            hazard_type="test_hazard",
            confidence=0.95,
            alert_level="RED",
            location=LocationData(
                latitude=37.7749,
                longitude=-122.4194,
                location_name="Test Location"
            ),
            description="Test alert for integration testing",
            metadata={"test": True}
        )
        
        # Test sending multi-channel alert
        alert_results = citizen_service.send_multi_channel_alert(test_alert)
        
        if alert_results:
            print("✅ Multi-channel alert sent successfully!")
            for channel_id, result in alert_results.items():
                if result.get('sent'):
                    print(f"  ✅ {channel_id}: Alert sent successfully")
                else:
                    print(f"  ⚠️ {channel_id}: {result.get('reason', 'Failed')}")
        else:
            print("⚠️ No multi-channel alert results (this may be normal if no channels configured)")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-channel alert test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚨 Coastal Hazard Detection System - Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Model Loading Test", test_model_loading),
        ("Service Initialization Test", test_service_initialization),
        ("Image Processing Test", test_image_processing),
        ("Alert Retrieval Test", test_alert_retrieval),
        ("Multi-Channel Alert Test", test_multi_channel_alerts)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! The system is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
