# CoastalGuard AI - Coastal Hazard Detection & Response System

A comprehensive AI-powered coastal hazard detection and response system designed to protect coastal communities through real-time monitoring, citizen reporting, and automated alert systems.

## 🚨 System Overview

CoastalGuard AI is a sophisticated coastal hazard management platform that combines machine learning, real-time monitoring, and multi-channel alerting to detect and respond to coastal hazards including:

- **Oil Spills & Hydrocarbon Contamination** - AI-powered detection using SAR-like features
- **Harmful Algal Blooms** - Environmental monitoring for water quality threats
- **Coastal Erosion** - Predictive modeling for shoreline changes
- **Marine Debris** - Detection and tracking of marine pollution
- **Water Pollution** - Comprehensive water quality monitoring
- **Coastal Flooding** - Real-time flood risk assessment

## 🏆 Hackathon Features

### 🎯 **Comprehensive Citizen Reporting System**
- **Quick Report Buttons** - One-click hazard reporting for emergency situations
- **Detailed Report Forms** - Comprehensive data collection with environmental conditions
- **Media Upload Support** - Photo and video evidence with drag-and-drop interface
- **Location Services** - GPS integration for precise hazard location
- **Contact Management** - Optional reporter information for follow-up
- **Real-time Validation** - Form validation and submission feedback

### 🚨 **Emergency Response Features**
- **Emergency Alert Banner** - Prominent display of high-priority alerts
- **Multi-Channel Alerting** - Email, SMS, IVR, Webhook, and Push notifications
- **Real-time Dashboard** - Live monitoring of system status and alerts
- **Alert Management** - Comprehensive alert tracking and management
- **Response Coordination** - Automated coordination with emergency services

### 🤖 **AI-Powered Detection**
- **Multiple ML Models** - Specialized models for different hazard types
- **Real-time Analysis** - Instant hazard assessment and classification
- **Confidence Scoring** - Probability-based risk assessment
- **Automated Alerts** - Intelligent alert triggering based on severity
- **Model Health Monitoring** - Continuous model performance tracking

### 📊 **Advanced Analytics**
- **Real-time Statistics** - Live system performance metrics
- **Activity Tracking** - Comprehensive audit trail of all reports
- **Trend Analysis** - Historical data analysis and pattern recognition
- **Performance Monitoring** - System response time and accuracy tracking

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Backend API   │    │   ML Models     │
│                 │    │                 │    │                 │
│ • Dashboard     │◄──►│ • Flask API     │◄──►│ • Oil Spill     │
│ • Citizen       │    │ • Joblib Models │    │ • Algal Bloom   │
│   Reporting     │    │ • Multi-Channel │    │ • Erosion       │
│ • Alert Mgmt    │    │   Alerts        │    │                 │
│ • Tide Monitor  │    │ • Geocoding     │    └─────────────────┘
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Tide API      │    │   Alert System  │
│                 │    │                 │
│ • Real-time     │    │ • Email Alerts  │
│   Tide Data     │    │ • SMS Alerts    │
│ • Forecasting   │    │ • IVR Calls     │
│ • Risk Assess   │    │ • Webhooks      │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Backend Setup
   ```bash
# Clone repository
   git clone <repository-url>
cd Team_Arceus_Hackout

# Install dependencies
   pip install -r requirements.txt

# Start backend API
python api.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Start frontend server
python server.py
```

### Full Stack Demo
```bash
# Terminal 1: Start backend
python api.py

# Terminal 2: Start frontend
cd frontend
python server.py

# Open browser to http://localhost:5000
```

## 📁 Project Structure

```
Team_Arceus_Hackout/
├── api.py                          # Main Flask API
├── citizen_reporting.py            # Citizen reporting service
├── multi_channel_alerts.py         # Multi-channel alert system
├── tide_api.py                     # Tide monitoring API
├── models/                         # Trained ML models
│   ├── oil_spill_rf.pkl
│   ├── algal_bloom_rf.pkl
│   └── coastal_erosion_rf.pkl
├── frontend/                       # Modern web interface
│   ├── index.html                  # Main application
│   ├── styles.css                  # Modern styling
│   ├── script.js                   # Interactive logic
│   └── server.py                   # Frontend server
├── data/                           # Training datasets
├── artifacts/                      # Model artifacts
└── requirements.txt                # Python dependencies
```

## 🎯 Hackathon Demo Flow

### **Option 1: Frontend Demo (Recommended)**
1. **Start the System** - Launch frontend server
2. **Dashboard Overview** - Show real-time statistics and system health
3. **Citizen Reporting Demo**:
   - Click "Quick Report" buttons for different hazards
   - Fill out comprehensive report form
   - Upload media evidence
   - Use location services
   - Submit report and show results
4. **Alert Management** - Display active alerts and response coordination
5. **Tide Monitoring** - Show real-time tide data and forecasting
6. **Emergency Response** - Demonstrate emergency alert system

### **Option 2: Full Stack Demo**
1. **Backend Health Check** - Verify API endpoints and model status
2. **Citizen Report Processing**:
   - Submit report through frontend
   - Show backend processing in real-time
   - Display ML model predictions
   - Trigger multi-channel alerts
3. **Alert System Demo** - Show email/SMS alert generation
4. **Data Flow Visualization** - Demonstrate end-to-end processing

### **Option 3: Backend-Only Demo**
1. **API Endpoints** - Test all endpoints with sample data
2. **ML Model Testing** - Run predictions with different inputs
3. **Alert System** - Demonstrate multi-channel alert capabilities
4. **Integration Testing** - Show system integration points

## 🔧 Configuration

### Environment Variables
```bash
# Copy example environment file
cp env.example .env

# Configure your settings
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

### API Endpoints
- `GET /health` - System health check
- `POST /predict` - ML model predictions
- `POST /upload` - Citizen report submission
- `GET /alerts` - Active alerts
- `GET /models` - Available ML models

## 🎨 Design System

### Color Palette
- **Primary**: `#667eea` (Coastal Blue)
- **Secondary**: `#764ba2` (Deep Purple)
- **Success**: `#10b981` (Emerald Green)
- **Warning**: `#f59e0b` (Amber)
- **Error**: `#ef4444` (Red)
- **Info**: `#3b82f6` (Blue)

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700
- **Responsive**: Mobile-first design approach

### Components
- **Cards**: Glassmorphism with backdrop blur
- **Buttons**: Gradient backgrounds with hover effects
- **Forms**: Modern input styling with validation
- **Alerts**: Color-coded alert levels
- **Navigation**: Sticky header with active states

## 📱 Responsive Design

The frontend is fully responsive and optimized for:
- **Desktop**: Full-featured interface with all capabilities
- **Tablet**: Touch-optimized interface
- **Mobile**: Streamlined interface for on-the-go reporting

## 🔒 Security Features

- **Input Validation** - Comprehensive form validation
- **File Upload Security** - Secure media file handling
- **API Rate Limiting** - Protection against abuse
- **Data Sanitization** - XSS and injection protection
- **HTTPS Ready** - Secure communication protocols

## 🧪 Testing

### Frontend Testing
```bash
# Run frontend tests
cd frontend
python -m pytest test_frontend.py
```

### Backend Testing
```bash
# Run backend tests
python -m pytest test_api.py
python -m pytest test_integration.py
```

### Manual Testing
- Test all form validations
- Verify file upload functionality
- Check responsive design
- Test alert system integration

## 📈 Performance

- **Frontend**: < 2s initial load time
- **API Response**: < 500ms for predictions
- **Image Processing**: < 3s for analysis
- **Alert Delivery**: < 30s for notifications

## 🔮 Future Enhancements

- **Mobile App** - Native iOS/Android applications
- **IoT Integration** - Sensor network integration
- **Satellite Data** - Real-time satellite imagery
- **Predictive Analytics** - Advanced forecasting models
- **Blockchain** - Immutable audit trail
- **AR/VR** - Augmented reality hazard visualization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For hackathon judges or technical questions:
- **Documentation**: Check this README
- **Issues**: Create a GitHub issue
- **Demo**: Follow the demo flow above

---

**Built for Hackathon Success** 🏆

This system is designed to showcase comprehensive coastal hazard management capabilities with a focus on citizen engagement, AI-powered detection, and emergency response coordination.
