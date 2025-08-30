#!/usr/bin/env python3
"""
Tide Monitoring Service for Coastal Hazard Detection System

This service provides:
- Real-time tide monitoring and predictions
- Integration with coastal hazard detection
- Hindu calendar-based tide analysis
- Weather correlation for coastal risk assessment
- API endpoints for tide data access
"""

import json
import datetime
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import math
import logging
from pathlib import Path

# Import existing tide prediction system
from tide_forecast_simple import (
    TidePredictor, 
    TidePrediction, 
    HinduCalendar, 
    TideCalculator,
    WeatherSimulator
)

# Import coastal hazard detection components
try:
    from citizen_reporting import CitizenReportingService
    from multi_channel_alerts import MultiChannelAlertService
    COASTAL_SYSTEM_AVAILABLE = True
except ImportError:
    COASTAL_SYSTEM_AVAILABLE = False
    logging.warning("Coastal hazard detection system not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TideAlert:
    """Tide alert data structure"""
    alert_id: str
    timestamp: datetime
    alert_type: str  # 'HIGH_TIDE', 'LOW_TIDE', 'STORM_SURGE', 'COASTAL_FLOODING'
    severity: str    # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    location: Dict[str, float]
    tide_height: float
    predicted_impact: str
    recommendations: List[str]
    expires_at: datetime
    is_active: bool = True

@dataclass
class CoastalRiskAssessment:
    """Comprehensive coastal risk assessment"""
    timestamp: datetime
    location: Dict[str, float]
    overall_risk: str
    tide_risk: Dict[str, Any]
    weather_risk: Dict[str, Any]
    hindu_calendar_risk: Dict[str, Any]
    combined_risk_score: float
    alerts_generated: List[str]
    recommendations: List[str]

class TideMonitoringService:
    """Main tide monitoring service"""
    
    def __init__(self, latitude: float, longitude: float, config_file: str = None):
        self.latitude = latitude
        self.longitude = longitude
        self.location_name = self._get_location_name()
        
        # Initialize tide prediction system
        self.tide_predictor = TidePredictor(latitude, longitude)
        self.hindu_calendar = HinduCalendar()
        
        # Initialize coastal hazard system if available
        self.coastal_service = None
        self.alert_service = None
        if COASTAL_SYSTEM_AVAILABLE:
            try:
                if config_file and Path(config_file).exists():
                    self.alert_service = MultiChannelAlertService(config_file)
                else:
                    self.alert_service = MultiChannelAlertService()
                self.coastal_service = CitizenReportingService(multi_channel_service=self.alert_service)
                logger.info("Coastal hazard detection system integrated")
            except Exception as e:
                logger.error(f"Failed to initialize coastal hazard system: {e}")
        
        # Tide monitoring state
        self.active_alerts: List[TideAlert] = []
        self.tide_history: List[TidePrediction] = []
        self.risk_assessments: List[CoastalRiskAssessment] = []
        
        # Configuration
        self.high_tide_threshold = 3.0  # meters
        self.low_tide_threshold = 0.5   # meters
        self.storm_surge_threshold = 4.0  # meters
        self.monitoring_interval = 3600  # seconds (1 hour)
        
        logger.info(f"Tide monitoring service initialized for {self.location_name}")
    
    def _get_location_name(self) -> str:
        """Get human-readable location name"""
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="tide_monitoring_service")
            location = geolocator.reverse(f"{self.latitude}, {self.longitude}")
            return location.address if location else f"Lat: {self.latitude}, Lon: {self.longitude}"
        except Exception:
            return f"Lat: {self.latitude}, Lon: {self.longitude}"
    
    def get_current_tide_status(self) -> Dict[str, Any]:
        """Get current tide status and immediate forecast"""
        now = datetime.now()
        
        # Get current tide prediction
        current_prediction = self._get_current_tide_prediction(now)
        
        # Get next 6 hours forecast
        next_6_hours = self._get_forecast_range(now, hours=6)
        
        # Calculate current risk level
        current_risk = self._assess_current_risk(current_prediction, next_6_hours)
        
        return {
            'timestamp': now.isoformat(),
            'location': {
                'name': self.location_name,
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'current_tide': {
                'height_meters': current_prediction.height_meters if current_prediction else None,
                'type': current_prediction.tide_type if current_prediction else None,
                'trend': self._get_tide_trend(next_6_hours),
                'next_change': self._get_next_tide_change(next_6_hours)
            },
            'risk_assessment': current_risk,
            'active_alerts': len([a for a in self.active_alerts if a.is_active]),
            'weather': current_prediction.weather_info if current_prediction else None,
            'hindu_calendar': current_prediction.hindu_factors if current_prediction else None
        }
    
    def _get_current_tide_prediction(self, time: datetime) -> Optional[TidePrediction]:
        """Get tide prediction for current time"""
        # Generate predictions for current day if not available
        if not self.tide_history or len(self.tide_history) == 0:
            self._update_tide_predictions()
        
        # Find closest prediction to current time
        if self.tide_history:
            closest = min(self.tide_history, key=lambda x: abs((x.timestamp - time).total_seconds()))
            if abs((closest.timestamp - time).total_seconds()) < 3600:  # Within 1 hour
                return closest
        
        return None
    
    def _get_forecast_range(self, start_time: datetime, hours: int = 24) -> List[TidePrediction]:
        """Get tide forecast for specified time range"""
        if not self.tide_history or len(self.tide_history) == 0:
            self._update_tide_predictions()
        
        end_time = start_time + timedelta(hours=hours)
        return [p for p in self.tide_history if start_time <= p.timestamp <= end_time]
    
    def _get_tide_trend(self, predictions: List[TidePrediction]) -> str:
        """Determine tide trend from predictions"""
        if len(predictions) < 2:
            return "stable"
        
        heights = [p.height_meters for p in predictions]
        if len(heights) >= 3:
            # Calculate trend over last 3 points
            recent_heights = heights[-3:]
            if recent_heights[0] < recent_heights[1] < recent_heights[2]:
                return "rising"
            elif recent_heights[0] > recent_heights[1] > recent_heights[2]:
                return "falling"
        
        return "stable"
    
    def _get_next_tide_change(self, predictions: List[TidePrediction]) -> Optional[Dict[str, Any]]:
        """Get information about next tide change"""
        if len(predictions) < 2:
            return None
        
        current_type = predictions[0].tide_type
        for pred in predictions[1:]:
            if pred.tide_type != current_type:
                return {
                    'type': pred.tide_type,
                    'timestamp': pred.timestamp.isoformat(),
                    'height': pred.height_meters,
                    'time_until': (pred.timestamp - datetime.now()).total_seconds() / 3600  # hours
                }
        
        return None
    
    def _assess_current_risk(self, current: Optional[TidePrediction], forecast: List[TidePrediction]) -> Dict[str, Any]:
        """Assess current coastal risk level"""
        risk_score = 0
        risk_factors = []
        
        if current:
            # Tide height risk
            if current.height_meters > self.storm_surge_threshold:
                risk_score += 5
                risk_factors.append("Storm surge conditions")
            elif current.height_meters > self.high_tide_threshold:
                risk_score += 3
                risk_factors.append("High tide conditions")
            
            # Weather risk
            if current.weather_info:
                if current.weather_info['condition'] == 'stormy':
                    risk_score += 4
                    risk_factors.append("Stormy weather")
                elif current.weather_info['condition'] == 'rainy':
                    risk_score += 2
                    risk_factors.append("Rainy conditions")
                
                # Wind risk
                try:
                    wind_speed = float(current.weather_info['wind_speed'].split()[0])
                    if wind_speed > 15:
                        risk_score += 3
                        risk_factors.append("High winds")
                    elif wind_speed > 10:
                        risk_score += 2
                        risk_factors.append("Moderate winds")
                except:
                    pass
        
        # Forecast risk
        for pred in forecast[:6]:  # Next 6 hours
            if pred.height_meters > self.high_tide_threshold:
                risk_score += 1
                risk_factors.append("High tide forecast")
        
        # Determine risk level
        if risk_score >= 8:
            risk_level = "CRITICAL"
        elif risk_score >= 6:
            risk_level = "HIGH"
        elif risk_score >= 4:
            risk_level = "MEDIUM"
        elif risk_score >= 2:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            'level': risk_level,
            'score': risk_score,
            'factors': list(set(risk_factors)),  # Remove duplicates
            'recommendations': self._get_risk_recommendations(risk_level, risk_factors)
        }
    
    def _get_risk_recommendations(self, risk_level: str, factors: List[str]) -> List[str]:
        """Get recommendations based on risk level and factors"""
        recommendations = []
        
        if risk_level == "CRITICAL":
            recommendations.extend([
                "Immediate evacuation of low-lying coastal areas",
                "Activate emergency response protocols",
                "Issue public safety announcements",
                "Monitor tide gauges continuously"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "Prepare for potential flooding",
                "Secure loose objects and boats",
                "Monitor weather updates",
                "Have emergency supplies ready"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "Exercise caution near water",
                "Monitor tide conditions",
                "Stay informed of weather changes"
            ])
        elif risk_level == "LOW":
            recommendations.extend([
                "Normal coastal activities",
                "Regular monitoring recommended"
            ])
        
        # Add specific factor-based recommendations
        if "High tide conditions" in factors:
            recommendations.append("Avoid low-lying coastal areas during high tide")
        if "Stormy weather" in factors:
            recommendations.append("Stay indoors and away from windows")
        if "High winds" in factors:
            recommendations.append("Secure outdoor objects and avoid coastal areas")
        
        return recommendations
    
    def _update_tide_predictions(self):
        """Update tide predictions for the next 7 days"""
        try:
            start_date = datetime.now()
            self.tide_history = self.tide_predictor.predict_tides(start_date, days=7)
            logger.info(f"Updated tide predictions: {len(self.tide_history)} predictions")
        except Exception as e:
            logger.error(f"Failed to update tide predictions: {e}")
    
    def generate_tide_alert(self, alert_type: str, severity: str, tide_data: Dict[str, Any]) -> TideAlert:
        """Generate a new tide alert"""
        alert_id = f"tide_{alert_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Set expiration time based on severity
        if severity == "CRITICAL":
            expires_in = timedelta(hours=2)
        elif severity == "HIGH":
            expires_in = timedelta(hours=4)
        elif severity == "MEDIUM":
            expires_in = timedelta(hours=6)
        else:
            expires_in = timedelta(hours=12)
        
        alert = TideAlert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            alert_type=alert_type,
            severity=severity,
            location={'latitude': self.latitude, 'longitude': self.longitude},
            tide_height=tide_data.get('height', 0),
            predicted_impact=tide_data.get('impact', 'Unknown'),
            recommendations=tide_data.get('recommendations', []),
            expires_at=datetime.now() + expires_in
        )
        
        self.active_alerts.append(alert)
        return alert
    
    def check_and_generate_alerts(self) -> List[TideAlert]:
        """Check current conditions and generate alerts if needed"""
        new_alerts = []
        current_status = self.get_current_tide_status()
        
        # Check for high tide alerts
        if current_status['current_tide']['height_meters']:
            height = current_status['current_tide']['height_meters']
            
            if height > self.storm_surge_threshold:
                alert = self.generate_tide_alert(
                    "STORM_SURGE", "CRITICAL",
                    {
                        'height': height,
                        'impact': 'Severe coastal flooding expected',
                        'recommendations': ['Immediate evacuation', 'Emergency response activation']
                    }
                )
                new_alerts.append(alert)
                
            elif height > self.high_tide_threshold:
                alert = self.generate_tide_alert(
                    "HIGH_TIDE", "HIGH",
                    {
                        'height': height,
                        'impact': 'Coastal flooding possible',
                        'recommendations': ['Avoid low-lying areas', 'Monitor conditions']
                    }
                )
                new_alerts.append(alert)
        
        # Check risk level changes
        risk_level = current_status['risk_assessment']['level']
        if risk_level in ["HIGH", "CRITICAL"]:
            # Check if we already have an active alert for this
            existing_risk_alerts = [a for a in self.active_alerts 
                                  if a.alert_type == "COASTAL_RISK" and a.is_active]
            
            if not existing_risk_alerts:
                alert = self.generate_tide_alert(
                    "COASTAL_RISK", risk_level,
                    {
                        'height': current_status['current_tide']['height_meters'] or 0,
                        'impact': f'Coastal risk level: {risk_level}',
                        'recommendations': current_status['risk_assessment']['recommendations']
                    }
                )
                new_alerts.append(alert)
        
        # Clean up expired alerts
        self._cleanup_expired_alerts()
        
        return new_alerts
    
    def _cleanup_expired_alerts(self):
        """Remove expired alerts"""
        now = datetime.now()
        for alert in self.active_alerts:
            if alert.expires_at < now:
                alert.is_active = False
        
        # Remove inactive alerts older than 24 hours
        cutoff_time = now - timedelta(hours=24)
        self.active_alerts = [a for a in self.active_alerts 
                             if a.is_active or a.timestamp > cutoff_time]
    
    def get_tide_forecast(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive tide forecast"""
        if not self.tide_history or len(self.tide_history) == 0:
            self._update_tide_predictions()
        
        if not self.tide_history:
            return {"error": "Failed to generate tide predictions"}
        
        # Get daily summaries
        daily_summaries = self._get_daily_summaries()
        
        # Get high/low tide times
        high_low_tides = self._get_high_low_tide_times()
        
        return {
            'location': {
                'name': self.location_name,
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'forecast_period': f"{days} days",
            'generated_at': datetime.now().isoformat(),
            'daily_summaries': daily_summaries,
            'high_low_tides': high_low_tides,
            'hindu_calendar_info': self._get_hindu_calendar_summary(),
            'weather_summary': self._get_weather_summary()
        }
    
    def _get_daily_summaries(self) -> List[Dict[str, Any]]:
        """Get daily tide summaries"""
        summaries = []
        current_date = None
        daily_predictions = []
        
        for pred in self.tide_history:
            pred_date = pred.timestamp.date()
            
            if current_date != pred_date:
                if current_date and daily_predictions:
                    summaries.append(self._create_daily_summary(current_date, daily_predictions))
                current_date = pred_date
                daily_predictions = []
            
            daily_predictions.append(pred)
        
        # Add last day
        if current_date and daily_predictions:
            summaries.append(self._create_daily_summary(current_date, daily_predictions))
        
        return summaries
    
    def _create_daily_summary(self, date: datetime.date, predictions: List[TidePrediction]) -> Dict[str, Any]:
        """Create summary for a single day"""
        heights = [p.height_meters for p in predictions]
        high_tides = [p for p in predictions if p.tide_type == 'high']
        low_tides = [p for p in predictions if p.tide_type == 'low']
        
        return {
            'date': date.isoformat(),
            'max_height': max(heights) if heights else 0,
            'min_height': min(heights) if heights else 0,
            'avg_height': sum(heights) / len(heights) if heights else 0,
            'high_tide_count': len(high_tides),
            'low_tide_count': len(low_tides),
            'hindu_date': predictions[0].hindu_factors if predictions else {},
            'weather_summary': self._get_daily_weather_summary(predictions)
        }
    
    def _get_daily_weather_summary(self, predictions: List[TidePrediction]) -> Dict[str, Any]:
        """Get weather summary for a day"""
        if not predictions:
            return {}
        
        conditions = [p.weather_info['condition'] for p in predictions if p.weather_info]
        temperatures = []
        wind_speeds = []
        
        for pred in predictions:
            if pred.weather_info:
                try:
                    temp = float(pred.weather_info['temperature'].split('°')[0])
                    temperatures.append(temp)
                except:
                    pass
                
                try:
                    wind = float(pred.weather_info['wind_speed'].split()[0])
                    wind_speeds.append(wind)
                except:
                    pass
        
        return {
            'primary_condition': max(set(conditions), key=conditions.count) if conditions else 'unknown',
            'avg_temperature': sum(temperatures) / len(temperatures) if temperatures else 0,
            'max_wind_speed': max(wind_speeds) if wind_speeds else 0
        }
    
    def _get_high_low_tide_times(self) -> List[Dict[str, Any]]:
        """Get high and low tide times for the forecast period"""
        high_low_tides = []
        
        for pred in self.tide_history:
            if pred.tide_type in ['high', 'low']:
                high_low_tides.append({
                    'timestamp': pred.timestamp.isoformat(),
                    'type': pred.tide_type,
                    'height_meters': pred.height_meters,
                    'hindu_factors': pred.hindu_factors
                })
        
        return high_low_tides[:20]  # Limit to first 20
    
    def _get_hindu_calendar_summary(self) -> Dict[str, Any]:
        """Get Hindu calendar summary for the forecast period"""
        if not self.tide_history:
            return {}
        
        # Get unique Hindu dates
        hindu_dates = set()
        for pred in self.tide_history:
            hindu_date = pred.hindu_factors
            hindu_dates.add((hindu_date['nakshatra'], hindu_date['tithi'], hindu_date['paksha']))
        
        return {
            'unique_nakshatras': list(set(date[0] for date in hindu_dates)),
            'unique_tithis': list(set(date[1] for date in hindu_dates)),
            'paksha_transitions': len([d for d in hindu_dates if d[2] == 'Shukla'])
        }
    
    def _get_weather_summary(self) -> Dict[str, Any]:
        """Get overall weather summary"""
        if not self.tide_history:
            return {}
        
        conditions = [p.weather_info['condition'] for p in self.tide_history if p.weather_info]
        wind_speeds = []
        
        for pred in self.tide_history:
            if pred.weather_info:
                try:
                    wind = float(pred.weather_info['wind_speed'].split()[0])
                    wind_speeds.append(wind)
                except:
                    pass
        
        return {
            'most_common_condition': max(set(conditions), key=conditions.count) if conditions else 'unknown',
            'max_wind_speed': max(wind_speeds) if wind_speeds else 0,
            'stormy_periods': conditions.count('stormy') if 'stormy' in conditions else 0
        }
    
    def export_data(self, format: str = 'json') -> str:
        """Export tide monitoring data"""
        if format.lower() == 'json':
            data = {
                'service_info': {
                    'name': 'Tide Monitoring Service',
                    'version': '1.0.0',
                    'location': self.location_name,
                    'coordinates': {'latitude': self.latitude, 'longitude': self.longitude}
                },
                'current_status': self.get_current_tide_status(),
                'forecast': self.get_tide_forecast(),
                'active_alerts': [asdict(alert) for alert in self.active_alerts if alert.is_active],
                'exported_at': datetime.now().isoformat()
            }
            
            # Convert datetime objects to ISO strings
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                return obj
            
            data = convert_datetime(data)
            
            output_file = f"tide_monitoring_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return output_file
        else:
            raise ValueError(f"Unsupported export format: {format}")


def main():
    """Main function for testing the tide monitoring service"""
    print("Tide Monitoring Service - Test Mode")
    print("=" * 50)
    
    # Initialize service for San Francisco Bay Area
    service = TideMonitoringService(latitude=37.7749, longitude=-122.4194)
    
    # Get current status
    print("\nCurrent Tide Status:")
    print("-" * 30)
    current_status = service.get_current_tide_status()
    print(f"Location: {current_status['location']['name']}")
    print(f"Current Tide: {current_status['current_tide']['height_meters']:.2f}m ({current_status['current_tide']['type']})")
    print(f"Risk Level: {current_status['risk_assessment']['level']}")
    print(f"Active Alerts: {current_status['active_alerts']}")
    
    # Check for alerts
    print("\nChecking for Alerts:")
    print("-" * 30)
    new_alerts = service.check_and_generate_alerts()
    if new_alerts:
        print(f"Generated {len(new_alerts)} new alerts:")
        for alert in new_alerts:
            print(f"  - {alert.alert_type} ({alert.severity}): {alert.predicted_impact}")
    else:
        print("No new alerts generated")
    
    # Get forecast
    print("\nTide Forecast Summary:")
    print("-" * 30)
    forecast = service.get_tide_forecast(days=3)
    if 'daily_summaries' in forecast:
        for day in forecast['daily_summaries'][:3]:
            print(f"  {day['date']}: Max {day['max_height']:.2f}m, Min {day['min_height']:.2f}m")
    
    # Export data
    print("\nExporting Data:")
    print("-" * 30)
    try:
        export_file = service.export_data('json')
        print(f"Data exported to: {export_file}")
    except Exception as e:
        print(f"Export failed: {e}")
    
    print("\nTide monitoring service test completed!")


if __name__ == "__main__":
    main()
