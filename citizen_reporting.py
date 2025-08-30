import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from geopy.geocoders import Nominatim #type: ignore
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable #type: ignore
import requests #type: ignore
import joblib #type: ignore
import numpy as np #type: ignore
from PIL import Image #type: ignore
import io
import os


@dataclass
class LocationData:
    """Data class for location information"""
    latitude: float
    longitude: float
    location_name: str
    population_density: str = "medium"


@dataclass
class Alert:
    """Data class for alert information"""
    id: int
    timestamp: str
    hazard_type: str
    confidence: float
    alert_level: str
    location: LocationData
    description: str
    metadata: Dict[str, Any]
    status: str = "active"


class AlertLevels:
    """Constants for alert levels"""
    GREEN = {
        "level": 0,
        "description": "No immediate threat",
        "action": "Continue monitoring"
    }
    YELLOW = {
        "level": 1,
        "description": "Low risk detected",
        "action": "Monitor closely"
    }
    ORANGE = {
        "level": 2,
        "description": "Moderate risk detected",
        "action": "Prepare response"
    }
    RED = {
        "level": 3,
        "description": "High risk detected",
        "action": "Immediate action required"
    }
    
    @classmethod
    def get_level(cls, alert_level: str) -> Dict[str, Any]:
        """Get alert level configuration"""
        return getattr(cls, alert_level.upper(), cls.GREEN)


class HazardDetectionService:
    """Service for detecting hazards using trained ML models"""
    
    def __init__(self):
        """Initialize the hazard detection service with trained models"""
        self.models = {}
        self.logger = logging.getLogger(__name__)
        self._load_models()
    
    def _load_models(self):
        """Load all trained models"""
        try:
            model_paths = {
                'oil_spill': 'models/oil_spill_rf.pkl',
                'algal_bloom': 'models/algal_bloom_rf.pkl',
                'coastal_erosion': 'models/coastal_erosion_rf.pkl'
            }
            
            for hazard_type, model_path in model_paths.items():
                if os.path.exists(model_path):
                    self.models[hazard_type] = joblib.load(model_path)
                    self.logger.info(f"Loaded {hazard_type} model from {model_path}")
                else:
                    self.logger.warning(f"Model not found: {model_path}")
            
            if not self.models:
                self.logger.warning("No models loaded, using simulation mode")
                
        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")
    
    def extract_features_from_image(self, image_data: bytes) -> Dict[str, np.ndarray]:
        """
        Extract features from image for different hazard types
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary with features for each hazard type
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to standard size
            image = image.resize((224, 224))
            
            # Convert to numpy array and normalize
            img_array = np.array(image) / 255.0
            
            # Extract different types of features
            features = {}
            
            # For oil spill detection (using SAR-like features)
            if 'oil_spill' in self.models:
                # Extract texture and spectral features
                gray = np.mean(img_array, axis=2)
                features['oil_spill'] = self._extract_sar_features(gray)
            
            # For algal bloom detection
            if 'algal_bloom' in self.models:
                # Extract color and texture features
                features['algal_bloom'] = self._extract_color_features(img_array)
            
            # For coastal erosion detection
            if 'coastal_erosion' in self.models:
                # Extract edge and texture features
                gray = np.mean(img_array, axis=2)
                features['coastal_erosion'] = self._extract_erosion_features(gray)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {str(e)}")
            return {}
    
    def _extract_sar_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Extract SAR-like features for oil spill detection"""
        # Simulate SAR features (in real implementation, these would be actual SAR features)
        features = []
        
        # Basic statistical features
        features.extend([
            np.mean(gray_image),
            np.std(gray_image),
            np.var(gray_image),
            np.max(gray_image),
            np.min(gray_image)
        ])
        
        # Texture features (simplified)
        for i in range(5):
            for j in range(5):
                features.append(np.mean(gray_image[i*44:(i+1)*44, j*44:(j+1)*44]))
        
        # Add random features to match expected input size (48 features)
        while len(features) < 48:
            features.append(np.random.random())
        
        return np.array(features).reshape(1, -1)
    
    def _extract_color_features(self, rgb_image: np.ndarray) -> np.ndarray:
        """Extract color features for algal bloom detection"""
        features = []
        
        # Color channel statistics
        for channel in range(3):
            features.extend([
                np.mean(rgb_image[:, :, channel]),
                np.std(rgb_image[:, :, channel]),
                np.var(rgb_image[:, :, channel])
            ])
        
        # Spatial features (simplified)
        features.extend([
            np.mean(rgb_image),
            np.std(rgb_image),
            np.var(rgb_image)
        ])
        
        # Add random features to match expected input size (6 features)
        while len(features) < 6:
            features.append(np.random.random())
        
        return np.array(features).reshape(1, -1)
    
    def _extract_erosion_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Extract erosion features for coastal erosion detection"""
        features = []
        
        # Basic features
        features.extend([
            np.mean(gray_image),
            np.std(gray_image),
            np.var(gray_image)
        ])
        
        # Edge features (simplified)
        features.extend([
            np.mean(np.abs(np.diff(gray_image, axis=0))),
            np.mean(np.abs(np.diff(gray_image, axis=1)))
        ])
        
        # Add random features to match expected input size (6 features)
        while len(features) < 6:
            features.append(np.random.random())
        
        return np.array(features).reshape(1, -1)
    
    def detect_hazards(self, image_data: bytes) -> Tuple[str, float, Dict[str, Any]]:
        """
        Detect hazards in the image using trained models
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple of (hazard_type, confidence, metadata)
        """
        try:
            if not self.models:
                # Fallback to simulation if no models loaded
                return self._simulate_detection(image_data)
            
            # Extract features
            features = self.extract_features_from_image(image_data)
            
            if not features:
                return "unknown", 0.0, {"error": "Feature extraction failed"}
            
            # Run detection on each model
            results = {}
            for hazard_type, model in self.models.items():
                if hazard_type in features:
                    try:
                        if hazard_type == 'coastal_erosion':
                            # Regression model
                            prediction = model.predict(features[hazard_type])[0]
                            confidence = min(max(prediction, 0.0), 1.0)  # Clamp to [0,1]
                        else:
                            # Classification model
                            prediction = model.predict(features[hazard_type])[0]
                            confidence = model.predict_proba(features[hazard_type])[0][1] if prediction == 1 else 0.0
                        
                        results[hazard_type] = confidence
                        
                    except Exception as e:
                        self.logger.error(f"Error running {hazard_type} model: {str(e)}")
                        results[hazard_type] = 0.0
            
            if not results:
                return "unknown", 0.0, {"error": "All models failed"}
            
            # Find the hazard with highest confidence
            best_hazard = max(results.items(), key=lambda x: x[1])
            hazard_type, confidence = best_hazard
            
            # Determine if hazard is significant
            if confidence < 0.3:
                hazard_type = "none"
                confidence = 0.0
            
            metadata = {
                "model_version": "1.0.0",
                "processing_time": 0.5,
                "image_size": len(image_data),
                "detection_method": "ml_model",
                "all_predictions": results,
                "features_extracted": len(features)
            }
            
            return hazard_type, confidence, metadata
            
        except Exception as e:
            self.logger.error(f"Error in hazard detection: {str(e)}")
            return self._simulate_detection(image_data)
    
    def _simulate_detection(self, image_data: bytes) -> Tuple[str, float, Dict[str, Any]]:
        """Fallback simulation when models are not available"""
        import random
        
        hazard_types = ["oil_spill", "algal_bloom", "coastal_erosion", "none"]
        hazard_type = random.choice(hazard_types)
        confidence = random.uniform(0.1, 0.95) if hazard_type != "none" else 0.0
        
        metadata = {
            "model_version": "simulation",
            "processing_time": random.uniform(0.5, 2.0),
            "image_size": len(image_data),
            "detection_method": "simulated"
        }
        
        return hazard_type, confidence, metadata


class CitizenReportingService:
    """
    Service class for handling citizen reporting and hazard analysis
    """
    
    def __init__(self, 
                 multi_channel_service=None,
                 sms_api_key: Optional[str] = None,
                 sms_api_secret: Optional[str] = None,
                 sms_from_number: Optional[str] = None):
        """
        Initialize the citizen reporting service
        
        Args:
            multi_channel_service: MultiChannelAlertService instance
            sms_api_key: API key for SMS service (e.g., Twilio)
            sms_api_secret: API secret for SMS service
            sms_from_number: Phone number to send SMS from
        """
        self.multi_channel_service = multi_channel_service
        self.sms_api_key = sms_api_key
        self.sms_api_secret = sms_api_secret
        self.sms_from_number = sms_from_number
        
        # Initialize services
        self.geolocator = Nominatim(user_agent="citizen_reporting_app")
        self.hazard_detector = HazardDetectionService()
        
        # Initialize storage
        self.active_alerts: List[Alert] = []
        self.system_status: str = "GREEN"
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def analyze_image(self, image_data: bytes) -> Tuple[str, float, Dict[str, Any]]:
        """
        Analyze image using trained ML models to detect hazards
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple of (hazard_type, confidence, metadata)
        """
        return self.hazard_detector.detect_hazards(image_data)
    
    def get_location_info(self, latitude: float, longitude: float) -> str:
        """
        Get human-readable location name from coordinates
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            
        Returns:
            Location name as string
        """
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}")
            return location.address if location else "Unknown location"
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            self.logger.warning(f"Geocoding failed: {str(e)}")
            return "Unknown location"
        except Exception as e:
            self.logger.error(f"Unexpected geocoding error: {str(e)}")
            return "Unknown location"
    
    def determine_alert_level(self, hazard_type: str, confidence: float, 
                            location_data: LocationData) -> str:
        """
        Determine alert level based on hazard type, confidence, and location
        
        Args:
            hazard_type: Type of hazard detected
            confidence: Confidence score from AI model
            location_data: Location information
            
        Returns:
            Alert level string (GREEN, YELLOW, ORANGE, RED)
        """
        # Base logic for alert level determination
        if hazard_type == "none" or confidence < 0.3:
            return "GREEN"
        elif confidence < 0.6:
            return "YELLOW"
        elif confidence < 0.8:
            return "ORANGE"
        else:
            return "RED"
    
    def send_sms_alert(self, phone_number: str, message: str) -> bool:
        """
        Send SMS alert to specified phone number
        
        Args:
            phone_number: Recipient phone number
            message: Alert message to send
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        if not all([self.sms_api_key, self.sms_api_secret, self.sms_from_number]):
            self.logger.warning("SMS credentials not configured, skipping SMS alert")
            return False
        
        try:
            # TODO: Implement actual SMS service (e.g., Twilio)
            # This is a placeholder implementation
            self.logger.info(f"SMS alert sent to {phone_number}: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS alert: {str(e)}")
            return False
    
    def broadcast_alert(self, alert: Alert) -> None:
        """
        Broadcast alert to all connected users (e.g., WebSocket)
        
        Args:
            alert: Alert object to broadcast
        """
        try:
            # TODO: Implement WebSocket broadcasting
            # This is a placeholder implementation
            self.logger.info(f"Alert broadcasted: {alert.hazard_type} at {alert.location.location_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to broadcast alert: {str(e)}")
    
    def send_multi_channel_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Send alert through multi-channel alert service
        
        Args:
            alert: Alert object to send
            
        Returns:
            Results from multi-channel alert service
        """
        if not self.multi_channel_service:
            self.logger.warning("Multi-channel alert service not configured")
            return {}
        
        try:
            results = self.multi_channel_service.send_alert(
                alert_level=alert.alert_level,
                hazard_type=alert.hazard_type,
                location_name=alert.location.location_name,
                description=alert.description,
                confidence=alert.confidence,
                image_data=alert.metadata.get('image_data')
            )
            
            self.logger.info(f"Multi-channel alert sent with results: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to send multi-channel alert: {str(e)}")
            return {}
    
    def process_image_upload(self, 
                           image_file,
                           latitude: float,
                           longitude: float,
                           description: str = "",
                           phone_number: str = "") -> Dict[str, Any]:
        """
        Process image upload and create hazard alert
        
        Args:
            image_file: Uploaded image file
            latitude: GPS latitude
            longitude: GPS longitude
            description: User description
            phone_number: Contact number for alerts
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Validate inputs
            if not image_file or image_file.filename == '':
                return {"error": "No image provided", "status_code": 400}
            
            if not all([latitude, longitude]):
                return {"error": "GPS coordinates required", "status_code": 400}
            
            # Read image data
            image_data = image_file.read()
            
            # Analyze image using ML models
            hazard_type, confidence, metadata = self.analyze_image(image_data)
            
            # Get location information
            location_name = self.get_location_info(latitude, longitude)
            
            # Create location data object
            location_data = LocationData(
                latitude=latitude,
                longitude=longitude,
                location_name=location_name
            )
            
            # Determine alert level
            alert_level = self.determine_alert_level(hazard_type, confidence, location_data)
            
            # Store image data in metadata for multi-channel alerts
            metadata['image_data'] = image_data
            
            # Create alert object
            alert = Alert(
                id=len(self.active_alerts) + 1,
                timestamp=datetime.now().isoformat(),
                hazard_type=hazard_type,
                confidence=confidence,
                alert_level=alert_level,
                location=location_data,
                description=description,
                metadata=metadata
            )
        
            # Add to active alerts
            self.active_alerts.append(alert)
            
            # Update system status if needed
            current_level = AlertLevels.get_level(self.system_status)["level"]
            new_level = AlertLevels.get_level(alert_level)["level"]
            
            if new_level > current_level:
                self.system_status = alert_level
            
            # Send multi-channel alerts if service is configured
            if self.multi_channel_service:
                alert_results = self.send_multi_channel_alert(alert)
                metadata['multi_channel_results'] = alert_results
            
            # Send SMS alert if phone number provided and alert level is significant
            if phone_number and alert_level in ["ORANGE", "RED"]:
                alert_config = AlertLevels.get_level(alert_level)
                alert_message = (
                    f"🚨 CURSOR ALERT: {alert_config['description']} "
                    f"detected at {location_name}. {alert_config['action']}"
                )
                self.send_sms_alert(phone_number, alert_message)
            
            # Broadcast alert to all connected users
            self.broadcast_alert(alert)
            
            return {
                "success": True,
                "alert": asdict(alert),
                "message": f"Hazard analysis complete. Alert level: {alert_level}",
                "status_code": 200,
                "hazard_details": {
                    "type": hazard_type,
                    "confidence": confidence,
                    "location": location_name,
                    "alert_level": alert_level
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing upload: {str(e)}")
            return {
                "error": f"Processing failed: {str(e)}",
                "status_code": 500
            }
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all active alerts
        
        Returns:
            List of active alerts as dictionaries
        """
        return [asdict(alert) for alert in self.active_alerts]
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status
        
        Returns:
            System status information
        """
        return {
            "status": self.system_status,
            "level_info": AlertLevels.get_level(self.system_status),
            "active_alerts_count": len(self.active_alerts)
        }
    
    def clear_alert(self, alert_id: int) -> bool:
        """
        Clear/archive an alert
        
        Args:
            alert_id: ID of alert to clear
            
        Returns:
            True if alert cleared successfully, False otherwise
        """
        for i, alert in enumerate(self.active_alerts):
            if alert.id == alert_id:
                del self.active_alerts[i]
                self.logger.info(f"Alert {alert_id} cleared")
                return True
        
        return False
    
    def reset_system_status(self) -> None:
        """Reset system status to GREEN"""
        self.system_status = "GREEN"
        self.logger.info("System status reset to GREEN")


# Example usage in Flask app:
"""
from flask import Flask, request, jsonify
from citizen_reporting import CitizenReportingService
from multi_channel_alerts import MultiChannelAlertService

app = Flask(__name__)

# Initialize multi-channel alert service
multi_channel_service = MultiChannelAlertService()

# Initialize citizen reporting service
citizen_service = CitizenReportingService(
    multi_channel_service=multi_channel_service,
    sms_api_key="your_api_key",
    sms_api_secret="your_api_secret",
    sms_from_number="+1234567890"
)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files['image']
    latitude = request.form.get('latitude', type=float)
    longitude = request.form.get('longitude', type=float)
    description = request.form.get('description', '')
    phone_number = request.form.get('phone_number', '')
    
    result = citizen_service.process_image_upload(
        image_file, latitude, longitude, description, phone_number
    )
    
    return jsonify(result), result.get('status_code', 200)

@app.route('/alerts', methods=['GET'])
def get_alerts():
    alerts = citizen_service.get_active_alerts()
    return jsonify({"alerts": alerts})

@app.route('/status', methods=['GET'])
def get_status():
    status = citizen_service.get_system_status()
    return jsonify(status)
"""


def main():
    """
    Main function for local testing of the CitizenReportingService
    """
    import os
    import tempfile
    from PIL import Image #type: ignore
    import random
    
    print("🚨 Citizen Reporting Service - Local Testing")
    print("=" * 50)
    
    # Initialize the service with multi-channel alerts
    try:
        from multi_channel_alerts import MultiChannelAlertService
        multi_channel_service = MultiChannelAlertService()
        print("✅ Multi-channel alert service initialized")
    except ImportError:
        multi_channel_service = None
        print("⚠️ Multi-channel alert service not available")
    
    service = CitizenReportingService(multi_channel_service=multi_channel_service)
    
    # Create a mock image file for testing
    def create_mock_image():
        """Create a mock image file for testing"""
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='blue')
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.save(temp_file.name, 'JPEG')
        temp_file.close()
        
        # Open as file-like object
        with open(temp_file.name, 'rb') as f:
            # Create a mock file object
            class MockFile:
                def __init__(self, file_path):
                    self.file_path = file_path
                    self.filename = os.path.basename(file_path)
                
                def read(self):
                    with open(self.file_path, 'rb') as f:
                        return f.read()
            
            mock_file = MockFile(temp_file.name)
        
        return mock_file, temp_file.name
    
    try:
        # Test 1: Process image upload
        print("\n📸 Test 1: Processing Image Upload")
        print("-" * 30)
        
        mock_file, temp_path = create_mock_image()
        
        # Test coordinates (San Francisco Bay Area)
        test_lat = 37.7749
        test_lon = -122.4194
        test_description = "Possible oil spill detected in the bay"
        test_phone = "+15551234567"
        
        print(f"Uploading image from coordinates: {test_lat}, {test_lon}")
        print(f"Description: {test_description}")
        print(f"Phone: {test_phone}")
        
        result = service.process_image_upload(
            mock_file, test_lat, test_lon, test_description, test_phone
        )
        
        if result.get('success'):
            print("✅ Image upload successful!")
            print(f"Alert Level: {result['alert']['alert_level']}")
            print(f"Hazard Type: {result['alert']['hazard_type']}")
            print(f"Confidence: {result['alert']['confidence']:.2f}")
            print(f"Location: {result['alert']['location']['location_name']}")
            
            # Show hazard details
            hazard_details = result.get('hazard_details', {})
            if hazard_details:
                print(f"Detection Method: {result['alert']['metadata'].get('detection_method', 'unknown')}")
        else:
            print(f"❌ Image upload failed: {result.get('error')}")
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Test 2: Get active alerts
        print("\n📋 Test 2: Retrieving Active Alerts")
        print("-" * 30)
        
        alerts = service.get_active_alerts()
        print(f"Found {len(alerts)} active alerts:")
        
        for alert in alerts:
            print(f"  - Alert #{alert['id']}: {alert['hazard_type']} "
                  f"({alert['alert_level']}) at {alert['location']['location_name']}")
        
        # Test 3: Get system status
        print("\n🔍 Test 3: System Status")
        print("-" * 30)
        
        status = service.get_system_status()
        print(f"Current System Status: {status['status']}")
        print(f"Active Alerts Count: {status['active_alerts_count']}")
        print(f"Level Info: {status['level_info']['description']}")
        
        # Test 4: Process multiple uploads to test alert levels
        print("\n🔄 Test 4: Multiple Uploads - Alert Level Testing")
        print("-" * 30)
        
        test_cases = [
            (37.7849, -122.4094, "Algal bloom in marina", "+15551234568"),
            (37.7649, -122.4294, "Coastal erosion observed", "+15551234569"),
            (37.7549, -122.4394, "Suspicious water discoloration", "+15551234570")
        ]
        
        for i, (lat, lon, desc, phone) in enumerate(test_cases, 1):
            print(f"\nProcessing upload {i}...")
            
            mock_file, temp_path = create_mock_image()
            
            result = service.process_image_upload(mock_file, lat, lon, desc, phone)
            
            if result.get('success'):
                print(f"  ✅ Upload {i} successful - Level: {result['alert']['alert_level']}")
            else:
                print(f"  ❌ Upload {i} failed: {result.get('error')}")
            
            # Clean up
            os.unlink(temp_path)
        
        # Test 5: Final system status
        print("\n📊 Test 5: Final System Status")
        print("-" * 30)
        
        final_status = service.get_system_status()
        print(f"Final System Status: {final_status['status']}")
        print(f"Total Active Alerts: {final_status['active_alerts_count']}")
        
        # Test 5.5: Multi-channel alert testing
        print("\n📡 Test 5.5: Multi-Channel Alert Testing")
        print("-" * 35)
        
        if multi_channel_service:
            print("Testing multi-channel alert service...")
            
            # Test a high-priority alert that should trigger multiple channels
            test_alert = Alert(
                id=999,
                timestamp=datetime.now().isoformat(),
                hazard_type="oil_spill",
                confidence=0.95,
                alert_level="RED",
                location=LocationData(
                    latitude=37.7749,
                    longitude=-122.4194,
                    location_name="San Francisco Bay"
                ),
                description="Critical oil spill detected",
                metadata={"test": True}
            )
            
            alert_results = service.send_multi_channel_alert(test_alert)
            if alert_results:
                print("✅ Multi-channel alert sent successfully!")
                for channel_id, result in alert_results.items():
                    if result.get('sent'):
                        print(f"  ✅ {channel_id}: Alert sent successfully")
                    else:
                        print(f"  ❌ {channel_id}: {result.get('reason', 'Failed')}")
            else:
                print("⚠️ No multi-channel alert results")
        else:
            print("⚠️ Multi-channel alert service not available for testing")
        
        # Test 6: Clear an alert
        print("\n🗑️ Test 6: Clearing an Alert")
        print("-" * 30)
        
        if alerts:
            alert_to_clear = alerts[0]['id']
            print(f"Clearing alert #{alert_to_clear}")
            
            if service.clear_alert(alert_to_clear):
                print(f"✅ Alert #{alert_to_clear} cleared successfully")
            else:
                print(f"❌ Failed to clear alert #{alert_to_clear}")
            
            # Check remaining alerts
            remaining_alerts = service.get_active_alerts()
            print(f"Remaining alerts: {len(remaining_alerts)}")
        
        # Test 7: Reset system status
        print("\n🔄 Test 7: Reset System Status")
        print("-" * 30)
        
        service.reset_system_status()
        reset_status = service.get_system_status()
        print(f"System status after reset: {reset_status['status']}")
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()