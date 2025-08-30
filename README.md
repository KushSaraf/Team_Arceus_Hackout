# Coastal Hazard Detection System

A comprehensive system for detecting and alerting about coastal hazards including oil spills, algal blooms, and coastal erosion using machine learning models and multi-channel alerting.

## 🚀 Quick Start

```bash
# 1. Install dependencies
make install

# 2. Train all ML models
make train

# 3. Start the unified API
make api

# 4. Test predictions
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"hazard_type": "algal_bloom", "features": {"LATITUDE": 37.7749, "LONGITUDE": -122.4194, "SALINITY": 35.0, "WATER_TEMP": 18.5, "WIND_SPEED": 12.0, "Month": 8}}'
```

## 🚀 Features

### Core Services
- **Citizen Reporting Service**: Processes image uploads and analyzes them for hazards
- **Multi-Channel Alert Service**: Sends alerts through multiple channels (Email, SMS, IVR, Webhook, Push)
- **Hazard Detection Service**: Uses trained ML models to detect hazards in images

### Alert Channels
- **Email Alerts**: HTML-formatted emails with image attachments
- **SMS Alerts**: Text messages via Twilio
- **IVR Alerts**: Voice calls with automated hazard announcements
- **Webhook Integration**: HTTP endpoints for external systems
- **Push Notifications**: Mobile app notifications (placeholder)

### Hazard Types
- **Oil Spill Detection**: Uses Random Forest classifier on SAR-like features
- **Algal Bloom Detection**: Analyzes color and environmental features
- **Coastal Erosion**: Regression model for erosion prediction

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Citizen App   │───▶│ Citizen Reporting│───▶│ Hazard Detection│
│   (Image + GPS) │    │     Service      │    │    Service      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Multi-Channel    │
                       │ Alert Service    │
                       └──────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   Email     │ │     SMS     │ │     IVR     │
        │   Alerts    │ │   Alerts    │ │   Alerts    │
        └─────────────┘ └─────────────┘ └─────────────┘
```

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd coastal-hazard-detection
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # Or use the Makefile
   make install
   ```

3. **Train the models** (if not already trained)
   ```bash
   # Train all models
   make train
   
   # Or train individually
   make train-oil
   make train-algal
   make train-erosion
   
   # Or manually
   python oil_spill_train.py
   python algal_blooms_train.py
   python coastal_erosion_train.py
   ```

## 🔧 Configuration

### Environment Setup

Copy the example environment file and configure your credentials:

```bash
# Copy the example file
cp env.example .env

# Edit with your actual credentials
nano .env
```

Required environment variables:
- `TWILIO_SID`: Your Twilio Account SID
- `TWILIO_TOKEN`: Your Twilio Auth Token  
- `TWILIO_FROM_NUMBER`: Your Twilio phone number
- `SMTP_HOST`: SMTP server (e.g., smtp.gmail.com)
- `SMTP_USER`: Your email username
- `SMTP_PASS`: Your email app password

**Note**: If credentials are missing, the system will gracefully disable those alert channels and log warnings.

### Multi-Channel Alert Service

Create a configuration file `alerts_config.json`:

```json
{
  "channels": {
    "email": {
      "name": "Email Alerts",
      "enabled": true,
      "priority_levels": ["ORANGE", "RED"],
      "config": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "your_email@gmail.com",
        "password": "your_app_password",
        "from_email": "alerts@yourdomain.com",
        "recipients": ["admin@yourdomain.com"]
      }
    },
    "sms": {
      "name": "SMS Alerts",
      "enabled": true,
      "priority_levels": ["RED"],
      "config": {
        "account_sid": "your_twilio_account_sid",
        "auth_token": "your_twilio_auth_token",
        "from_number": "+1234567890",
        "recipients": ["+15551234567"]
      }
    },
    "ivr": {
      "name": "IVR Voice Calls",
      "enabled": true,
      "priority_levels": ["RED"],
      "config": {
        "account_sid": "your_twilio_account_sid",
        "auth_token": "your_twilio_auth_token",
        "from_number": "+1234567890",
        "recipients": ["+15551234567"],
        "webhook_url": "https://your-domain.com/webhook",
        "voice": "alice",
        "language": "en-US"
      }
    }
  }
}
```

## 🚀 Usage

### Unified ML API

The system now includes a unified API (`api.py`) that provides a single endpoint for all ML predictions:

```bash
# Start the API server
python api.py
```

#### API Endpoints

**Health Check**
```bash
GET /health
```
Returns system status and loaded models.

**Make Predictions**
```bash
POST /predict
Content-Type: application/json

{
  "hazard_type": "algal_bloom",
  "features": {
    "LATITUDE": 37.7749,
    "LONGITUDE": -122.4194,
    "SALINITY": 35.0,
    "WATER_TEMP": 18.5,
    "WIND_SPEED": 12.0,
    "Month": 8
  }
}
```

**List Available Models**
```bash
GET /models
```
Returns information about all available models and their status.

**Get Required Features**
```bash
GET /features/algal_bloom
```
Returns the required features for a specific hazard type.

#### Sample API Requests

**Oil Spill Detection**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "hazard_type": "oil_spill",
    "features": {
      "f_1": 0.5,
      "f_2": 0.3,
      "f_3": 0.8,
      "f_4": 0.2,
      "f_5": 0.6
    }
  }'
```

**Algal Bloom Detection**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "hazard_type": "algal_bloom",
    "features": {
      "LATITUDE": 37.7749,
      "LONGITUDE": -122.4194,
      "SALINITY": 35.0,
      "WATER_TEMP": 18.5,
      "WIND_SPEED": 12.0,
      "Month": 8
    }
  }'
```

**Coastal Erosion Prediction**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "hazard_type": "coastal_erosion",
    "features": {
      "Category_o": 1,
      "Nature_of_": 2,
      "Status": 1,
      "Water_Leve": 3,
      "Scale_Mini": 0.5,
      "SHAPE_Leng": 150.0
    }
  }'
```

#### Expected Responses

**Successful Prediction**
```json
{
  "hazard_type": "algal_bloom",
  "prediction": 1,
  "probability": 0.85,
  "features_used": ["LATITUDE", "LONGITUDE", "SALINITY", "WATER_TEMP", "WIND_SPEED", "Month"],
  "timestamp": "2024-01-15T10:30:00",
  "model_info": {
    "type": "RandomForestClassifier",
    "features_count": 6
  }
}
```

**Error Response**
```json
{
  "error": "missing features: ['LATITUDE', 'SALINITY']",
  "required": ["LATITUDE", "LONGITUDE", "SALINITY", "WATER_TEMP", "WIND_SPEED", "Month"],
  "received": ["LONGITUDE", "WATER_TEMP", "WIND_SPEED", "Month"]
}
```

### Flask Application

```python
from flask import Flask, request, jsonify
from citizen_reporting import CitizenReportingService
from multi_channel_alerts import MultiChannelAlertService

app = Flask(__name__)

# Initialize services
multi_channel_service = MultiChannelAlertService("alerts_config.json")
citizen_service = CitizenReportingService(multi_channel_service=multi_channel_service)

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

if __name__ == '__main__':
    app.run(debug=True)
```

### Direct Service Usage

```python
from citizen_reporting import CitizenReportingService
from multi_channel_alerts import MultiChannelAlertService

# Initialize services
multi_channel_service = MultiChannelAlertService()
citizen_service = CitizenReportingService(multi_channel_service=multi_channel_service)

# Process an image
with open('hazard_image.jpg', 'rb') as f:
    result = citizen_service.process_image_upload(
        image_file=f,
        latitude=37.7749,
        longitude=-122.4194,
        description="Possible oil spill",
        phone_number="+15551234567"
    )

print(f"Hazard detected: {result['hazard_details']['type']}")
print(f"Alert level: {result['hazard_details']['alert_level']}")
```

## 🧪 Testing

### Quick Tests
```bash
# Test individual services
python citizen_reporting.py
python multi_channel_alerts.py

# Test thermal camera detection
python thermal_camera_detection.py
```

### Integration Testing
```bash
# Run comprehensive integration tests
python test_integration.py
```

The integration test script (`test_integration.py`) will:
- ✅ Verify all imports work correctly
- ✅ Test ML model loading
- ✅ Validate service initialization
- ✅ Test complete image processing pipeline
- ✅ Verify alert retrieval functionality
- ✅ Test multi-channel alert integration

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing (planned)

## 📊 Alert Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **GREEN** | No immediate threat | Continue monitoring |
| **YELLOW** | Low risk detected | Monitor closely |
| **ORANGE** | Moderate risk detected | Prepare response |
| **RED** | High risk detected | Immediate action required |

## 🔌 Alert Channel Priorities

- **Email**: ORANGE, RED alerts
- **SMS**: RED alerts only
- **IVR**: RED alerts only
- **Webhook**: YELLOW, ORANGE, RED alerts
- **Push**: Configurable for all levels

## 📁 Project Structure

```
coastal-hazard-detection/
├── citizen_reporting.py          # Main citizen reporting service
├── multi_channel_alerts.py       # Multi-channel alert service
├── oil_spill_train.py           # Oil spill model training
├── algal_blooms_train.py        # Algal bloom model training
├── coastal_erosion_train.py     # Coastal erosion model training
├── models/                      # Trained ML models
│   ├── oil_spill_rf.pkl
│   ├── algal_bloom_rf.pkl
│   └── coastal_erosion_rf.pkl
├── data/                        # Training datasets
│   ├── oil_spill.csv
│   ├── algal_bloom.csv
│   └── shoreline.csv
├── artifacts/                   # Training results
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## ⚠️ Current Limitations & Known Issues

### 🔴 **Critical Issues**
- **Synthetic Training Data**: The coastal erosion model uses synthetic target variables created from existing features. This is acceptable for demonstration purposes but should not be used in production without real erosion measurements.
- **Model Accuracy**: Current ML models are basic Random Forest implementations and may need retraining with more data
- **Feature Extraction**: Image feature extraction is simplified and may not capture all relevant patterns
- **Error Handling**: Limited error handling for edge cases and network failures
- **Security**: No authentication or rate limiting implemented

### 🟡 **Performance Considerations**
- **Image Processing**: Large images may cause memory issues
- **Geocoding**: Nominatim geocoding service has rate limits
- **Alert Delivery**: No guaranteed delivery for critical alerts
- **Scalability**: Single-threaded processing may bottleneck under high load

### 🟠 **Missing Features**
- **Database**: No persistent storage for alerts or user data
- **User Management**: No user authentication or role-based access
- **API Documentation**: No OpenAPI/Swagger documentation
- **Monitoring**: No health checks or performance metrics
- **Logging**: Basic logging without structured logging or log aggregation

## 🔐 Environment Variables

Set these environment variables for production:

```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export SMTP_USERNAME="your_email"
export SMTP_PASSWORD="your_app_password"
```

## 🚨 Emergency Contacts

For critical alerts, the system will:
1. Send immediate SMS alerts to emergency contacts
2. Make voice calls (IVR) to key personnel
3. Send detailed email reports with images
4. Log all actions for audit purposes

## 🚀 Deployment

### Local Development
```bash
# Clone and setup
git clone <repository-url>
cd coastal-hazard-detection
pip install -r requirements.txt

# Run tests
python test_integration.py

# Start Flask app
python -c "
from citizen_reporting import CitizenReportingService
from multi_channel_alerts import MultiChannelAlertService
from flask import Flask, request, jsonify

app = Flask(__name__)
multi_channel_service = MultiChannelAlertService()
citizen_service = CitizenReportingService(multi_channel_service=multi_channel_service)

@app.route('/upload', methods=['POST'])
def upload_image():
    # Implementation here
    pass

if __name__ == '__main__':
    app.run(debug=True)
"
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=production
export FLASK_APP=app.py

# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker Deployment (Planned)
```dockerfile
# Dockerfile will be added in future updates
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔧 Troubleshooting

### Common Issues

#### **Import Errors**
```bash
# If you get import errors, ensure all dependencies are installed
pip install -r requirements.txt

# For specific packages
pip install opencv-python  # If OpenCV fails
pip install twilio         # If Twilio fails
```

#### **Model Loading Issues**
```bash
# Check if models exist
ls -la models/

# If models are missing, train them first
python oil_spill_train.py
python algal_blooms_train.py
python coastal_erosion_train.py
```

#### **Alert Service Failures**
```bash
# Check configuration
cat alerts_config.json

# Test individual channels
python multi_channel_alerts.py
```

#### **Performance Issues**
- Reduce image size before processing
- Check system memory usage
- Monitor geocoding API rate limits

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python test_integration.py
```

## 🎯 Judge-Proof Demo Flow

For hackathon judges and demonstrations, follow this sequence:

### 1. **Show Training Results**
```bash
# Display confusion matrices and metrics
ls -la artifacts/*/
cat artifacts/algal_blooms/metrics.json
cat artifacts/oil_spill/metrics.json
```

### 2. **Live API Demo**
```bash
# Start the API
make api

# In another terminal, test predictions
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"hazard_type": "algal_bloom", "features": {"LATITUDE": 37.7749, "LONGITUDE": -122.4194, "SALINITY": 35.0, "WATER_TEMP": 18.5, "WIND_SPEED": 12.0, "Month": 8}}'
```

### 3. **Alert System Demo**
```bash
# Test alert generation (will show "would send" if no credentials)
python -c "
from multi_channel_alerts import MultiChannelAlertService
service = MultiChannelAlertService()
result = service.send_alert('RED', 'oil_spill', 'San Francisco Bay', 'Large oil slick detected', 0.95)
print('Alert results:', result)
"
```

### 4. **Tide Monitoring**
```bash
# Show tide API functionality
python tide_api.py
# Visit http://localhost:5000 in browser
```

### 5. **Integration Test**
```bash
# Run the full pipeline test
python test_integration.py
```

## 🔮 Future Enhancements

### 🚧 **In Progress / Partially Implemented**
- [x] **Multi-channel alert system** - ✅ Complete with Email, SMS, IVR, Webhook, Push
- [x] **ML model integration** - ✅ Complete with oil spill, algal bloom, and coastal erosion detection
- [x] **Thermal camera detection** - ✅ Basic implementation for person detection
- [x] **Citizen reporting service** - ✅ Complete with image processing and alert generation

### 🚀 **Planned Features**
- [ ] **Real-time satellite data integration** - Connect to satellite APIs for automated monitoring
- [ ] **Advanced computer vision models** - Implement CNN-based detection for better accuracy
- [ ] **Mobile app development** - Native iOS/Android apps for citizen reporting
- [ ] **Weather data correlation** - Integrate weather APIs to correlate hazards with conditions
- [ ] **Historical trend analysis** - Database for tracking hazard patterns over time
- [ ] **API rate limiting and authentication** - Secure API endpoints with user management
- [ ] **Database persistence for alerts** - PostgreSQL/MongoDB for alert storage
- [ ] **WebSocket real-time updates** - Live updates for connected clients
- [ ] **Geofencing alerts** - Location-based alert targeting
- [ ] **Machine learning model retraining** - Automated model updates with new data
- [ ] **Multi-language support** - Internationalization for global deployment
- [ ] **Advanced analytics dashboard** - Web-based monitoring and reporting interface
- [ ] **Integration with emergency services** - Direct connection to 911/dispatch systems
- [ ] **Drone integration** - Automated aerial monitoring and image capture
- [ ] **Blockchain verification** - Immutable record of citizen reports and responses

### 🔧 **Technical Improvements Needed**
- [ ] **Error handling** - More robust error handling and recovery mechanisms
- [ ] **Performance optimization** - Caching, async processing, load balancing
- [ ] **Security hardening** - Input validation, SQL injection prevention, XSS protection
- [ ] **Testing coverage** - Unit tests, integration tests, end-to-end tests
- [ ] **Documentation** - API documentation, deployment guides, user manuals
- [ ] **Monitoring and logging** - Application performance monitoring, centralized logging
- [ ] **Containerization** - Docker containers for easy deployment
- [ ] **CI/CD pipeline** - Automated testing and deployment
