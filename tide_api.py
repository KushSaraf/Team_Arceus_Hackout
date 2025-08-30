#!/usr/bin/env python3
"""
Tide Monitoring API

Flask-based REST API for the tide monitoring service, providing:
- Real-time tide status
- Tide forecasts
- Alert management
- Risk assessments
- Data export capabilities
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import os

# Import tide monitoring service
from tide_monitoring_service import TideMonitoringService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global tide monitoring service instance
tide_service = None

def initialize_tide_service():
    """Initialize the tide monitoring service"""
    global tide_service
    
    # Get configuration from environment variables or use defaults
    latitude = float(os.getenv('TIDE_LATITUDE', '37.7749'))  # San Francisco default
    longitude = float(os.getenv('TIDE_LONGITUDE', '-122.4194'))
    config_file = os.getenv('ALERTS_CONFIG_FILE', 'alerts_config.json')
    
    try:
        tide_service = TideMonitoringService(
            latitude=latitude,
            longitude=longitude,
            config_file=config_file if Path(config_file).exists() else None
        )
        logger.info(f"Tide monitoring service initialized for coordinates: {latitude}, {longitude}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize tide monitoring service: {e}")
        return False

def setup():
    """Setup function called before first request"""
    if not initialize_tide_service():
        logger.error("Failed to initialize tide service - API will not function properly")

# Initialize service on startup
setup()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    if tide_service is None:
        return jsonify({
            'status': 'unhealthy',
            'error': 'Tide monitoring service not initialized',
            'timestamp': datetime.now().isoformat()
        }), 503
    
    return jsonify({
        'status': 'healthy',
        'service': 'Tide Monitoring API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'location': tide_service.location_name
    })

@app.route('/api/v1/tide/status', methods=['GET'])
def get_current_tide_status():
    """Get current tide status and immediate forecast"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        status = tide_service.get_current_tide_status()
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error getting tide status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tide/forecast', methods=['GET'])
def get_tide_forecast():
    """Get tide forecast for specified period"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        # Get forecast period from query parameters
        days = request.args.get('days', default=7, type=int)
        days = min(max(days, 1), 14)  # Limit to 1-14 days
        
        forecast = tide_service.get_tide_forecast(days=days)
        return jsonify(forecast)
    
    except Exception as e:
        logger.error(f"Error getting tide forecast: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tide/alerts', methods=['GET'])
def get_alerts():
    """Get current active alerts"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        # Get alert type filter from query parameters
        alert_type = request.args.get('type', default=None, type=str)
        severity = request.args.get('severity', default=None, type=str)
        
        alerts = tide_service.active_alerts
        
        # Apply filters
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Convert to serializable format
        serialized_alerts = []
        for alert in alerts:
            if alert.is_active:
                serialized_alerts.append({
                    'alert_id': alert.alert_id,
                    'timestamp': alert.timestamp.isoformat(),
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'location': alert.location,
                    'tide_height': alert.tide_height,
                    'predicted_impact': alert.predicted_impact,
                    'recommendations': alert.recommendations,
                    'expires_at': alert.expires_at.isoformat(),
                    'is_active': alert.is_active
                })
        
        return jsonify({
            'alerts': serialized_alerts,
            'total_count': len(serialized_alerts),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tide/alerts/check', methods=['POST'])
def check_and_generate_alerts():
    """Check current conditions and generate new alerts"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        # Check for new alerts
        new_alerts = tide_service.check_and_generate_alerts()
        
        # Convert to serializable format
        serialized_alerts = []
        for alert in new_alerts:
            serialized_alerts.append({
                'alert_id': alert.alert_id,
                'timestamp': alert.timestamp.isoformat(),
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'location': alert.location,
                'tide_height': alert.tide_height,
                'predicted_impact': alert.predicted_impact,
                'recommendations': alert.recommendations,
                'expires_at': alert.expires_at.isoformat()
            })
        
        return jsonify({
            'new_alerts': serialized_alerts,
            'count': len(serialized_alerts),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tide/risk-assessment', methods=['GET'])
def get_risk_assessment():
    """Get comprehensive coastal risk assessment"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        # Get current status which includes risk assessment
        status = tide_service.get_current_tide_status()
        
        # Get forecast for additional context
        forecast = tide_service.get_tide_forecast(days=3)
        
        risk_assessment = {
            'timestamp': datetime.now().isoformat(),
            'location': status['location'],
            'current_risk': status['risk_assessment'],
            'forecast_risk': {
                'next_24h': _assess_forecast_risk(forecast, hours=24),
                'next_48h': _assess_forecast_risk(forecast, hours=48),
                'next_72h': _assess_forecast_risk(forecast, hours=72)
            },
            'active_alerts_count': status['active_alerts'],
            'recommendations': status['risk_assessment']['recommendations']
        }
        
        return jsonify(risk_assessment)
    
    except Exception as e:
        logger.error(f"Error getting risk assessment: {e}")
        return jsonify({'error': str(e)}), 500

def _assess_forecast_risk(forecast: dict, hours: int) -> dict:
    """Assess risk for a specific forecast period"""
    if 'daily_summaries' not in forecast:
        return {'level': 'UNKNOWN', 'score': 0, 'factors': []}
    
    # Calculate risk based on forecast data
    risk_score = 0
    factors = []
    
    # Check for high tides in forecast
    if 'high_low_tides' in forecast:
        for tide in forecast['high_low_tides']:
            if tide['type'] == 'high' and tide['height_meters'] > 3.0:
                risk_score += 2
                factors.append("High tide forecast")
    
    # Determine risk level
    if risk_score >= 6:
        level = "HIGH"
    elif risk_score >= 4:
        level = "MEDIUM"
    elif risk_score >= 2:
        level = "LOW"
    else:
        level = "MINIMAL"
    
    return {
        'level': level,
        'score': risk_score,
        'factors': list(set(factors))
    }

@app.route('/api/v1/tide/export', methods=['GET'])
def export_tide_data():
    """Export tide monitoring data"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        # Get export format from query parameters
        export_format = request.args.get('format', default='json', type=str)
        
        if export_format.lower() != 'json':
            return jsonify({'error': 'Only JSON export is supported'}), 400
        
        # Export data
        export_file = tide_service.export_data(export_format)
        
        # Return the file for download
        return send_file(
            export_file,
            as_attachment=True,
            download_name=f"tide_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mimetype='application/json'
        )
    
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tide/hindu-calendar', methods=['GET'])
def get_hindu_calendar_info():
    """Get Hindu calendar information for tide analysis"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        # Get current status
        status = tide_service.get_current_tide_status()
        
        # Get forecast for Hindu calendar summary
        forecast = tide_service.get_tide_forecast(days=7)
        
        hindu_info = {
            'current': status.get('hindu_calendar', {}),
            'forecast_summary': forecast.get('hindu_calendar_info', {}),
            'tide_influence': _get_tide_influence(status.get('hindu_calendar', {})),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(hindu_info)
    
    except Exception as e:
        logger.error(f"Error getting Hindu calendar info: {e}")
        return jsonify({'error': str(e)}), 500

def _get_tide_influence(hindu_date: dict) -> dict:
    """Get tide influence based on Hindu calendar factors"""
    if not hindu_date:
        return {}
    
    try:
        # Use the Hindu calendar from the tide service
        hindu_calendar = tide_service.hindu_calendar
        tide_influence = hindu_calendar.get_tide_influence(hindu_date)
        
        return {
            'nakshatra_influence': tide_influence.get('nakshatra_tide', {}),
            'tithi_amplification': tide_influence.get('tithi_amplification', 1.0),
            'overall_strength': tide_influence.get('overall_strength', 'moderate'),
            'risk_level': tide_influence.get('risk_level', 'medium'),
            'recommendation': tide_influence.get('recommendation', 'Normal monitoring')
        }
    except Exception as e:
        logger.error(f"Error calculating tide influence: {e}")
        return {}

@app.route('/api/v1/tide/weather', methods=['GET'])
def get_weather_info():
    """Get weather information for tide correlation"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        # Get current status
        status = tide_service.get_current_tide_status()
        
        # Get forecast for weather summary
        forecast = tide_service.get_tide_forecast(days=3)
        
        weather_info = {
            'current': status.get('weather', {}),
            'forecast_summary': forecast.get('weather_summary', {}),
            'daily_weather': _extract_daily_weather(forecast),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(weather_info)
    
    except Exception as e:
        logger.error(f"Error getting weather info: {e}")
        return jsonify({'error': str(e)}), 500

def _extract_daily_weather(forecast: dict) -> list:
    """Extract daily weather information from forecast"""
    daily_weather = []
    
    if 'daily_summaries' in forecast:
        for day in forecast['daily_summaries']:
            if 'weather_summary' in day:
                daily_weather.append({
                    'date': day['date'],
                    'weather': day['weather_summary']
                })
    
    return daily_weather

@app.route('/api/v1/tide/statistics', methods=['GET'])
def get_tide_statistics():
    """Get statistical information about tides"""
    try:
        if tide_service is None:
            return jsonify({'error': 'Service not available'}), 503
        
        # Get forecast for statistics
        forecast = tide_service.get_tide_forecast(days=7)
        
        if 'daily_summaries' not in forecast:
            return jsonify({'error': 'No forecast data available'}), 500
        
        # Calculate statistics
        all_heights = []
        high_tide_heights = []
        low_tide_heights = []
        
        for day in forecast['daily_summaries']:
            all_heights.extend([day['max_height'], day['min_height']])
            high_tide_heights.append(day['max_height'])
            low_tide_heights.append(day['min_height'])
        
        if all_heights:
            statistics = {
                'overall': {
                    'max_height': max(all_heights),
                    'min_height': min(all_heights),
                    'avg_height': sum(all_heights) / len(all_heights),
                    'height_range': max(all_heights) - min(all_heights)
                },
                'high_tides': {
                    'max_height': max(high_tide_heights),
                    'min_height': min(high_tide_heights),
                    'avg_height': sum(high_tide_heights) / len(high_tide_heights)
                },
                'low_tides': {
                    'max_height': max(low_tide_heights),
                    'min_height': min(low_tide_heights),
                    'avg_height': sum(low_tide_heights) / len(low_tide_heights)
                },
                'period': '7 days',
                'timestamp': datetime.now().isoformat()
            }
        else:
            statistics = {'error': 'No height data available'}
        
        return jsonify(statistics)
    
    except Exception as e:
        logger.error(f"Error getting tide statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/health',
            '/api/v1/tide/status',
            '/api/v1/tide/forecast',
            '/api/v1/tide/alerts',
            '/api/v1/tide/alerts/check',
            '/api/v1/tide/risk-assessment',
            '/api/v1/tide/export',
            '/api/v1/tide/hindu-calendar',
            '/api/v1/tide/weather',
            '/api/v1/tide/statistics'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Initialize service before starting Flask
    if initialize_tide_service():
        logger.info("Starting Tide Monitoring API...")
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('TIDE_API_PORT', 5001)),
            debug=os.getenv('FLASK_ENV') == 'development'
        )
    else:
        logger.error("Failed to initialize tide service - cannot start API")
