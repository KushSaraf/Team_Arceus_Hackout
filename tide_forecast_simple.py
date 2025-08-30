#!/usr/bin/env python3
"""
Tide and Weather Forecasting System with Hindu Calendar Integration

A simplified but functional system that provides:
- Tide predictions based on astronomical calculations
- Weather forecasting (simulated or real API)
- Hindu calendar tide cycles (Nakshatra-based)
- Coastal hazard correlation
"""

import math
import datetime
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os

# Data classes for structured data
@dataclass
class TidePrediction:
    timestamp: datetime
    height_meters: float
    tide_type: str  # 'high', 'low', 'rising', 'falling'
    confidence: float
    hindu_factors: Dict[str, str]
    weather_info: Optional[Dict[str, str]] = None

@dataclass
class WeatherData:
    timestamp: datetime
    temperature: float
    condition: str
    wind_speed: float
    humidity: float

class HinduCalendar:
    """Hindu calendar calculations for tide cycles"""
    
    def __init__(self):
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        
        self.tithis = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
            "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
            "Trayodashi", "Chaturdashi", "Purnima", "Pratipada", "Dwitiya", "Tritiya",
            "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami",
            "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
        ]
    
    def get_current_hindu_date(self, date: datetime) -> Dict[str, str]:
        """Get current Hindu calendar date"""
        # Simplified calculation - in production use proper astronomical algorithms
        day_of_month = date.day
        month = date.month
        
        # Tithi (lunar day)
        tithi_num = (day_of_month - 1) % 30
        tithi = self.tithis[tithi_num]
        
        # Nakshatra (lunar mansion)
        nakshatra_num = (day_of_month - 1) % 27
        nakshatra = self.nakshatras[nakshatra_num]
        
        # Paksha (lunar fortnight)
        paksha = "Shukla" if tithi_num < 15 else "Krishna"
        
        return {
            'tithi': tithi,
            'nakshatra': nakshatra,
            'paksha': paksha,
            'lunar_day': tithi_num + 1
        }
    
    def get_tide_influence(self, hindu_date: Dict[str, str]) -> Dict[str, str]:
        """Get tide influence based on Hindu calendar"""
        nakshatra = hindu_date['nakshatra']
        tithi = hindu_date['tithi']
        
        # Nakshatra-based tide characteristics
        nakshatra_tides = {
            "Ashwini": {"strength": "strong", "direction": "rising", "risk": "high"},
            "Bharani": {"strength": "moderate", "direction": "rising", "risk": "medium"},
            "Krittika": {"strength": "strong", "direction": "high", "risk": "high"},
            "Rohini": {"strength": "moderate", "direction": "falling", "risk": "medium"},
            "Mrigashira": {"strength": "weak", "direction": "low", "risk": "low"},
            "Ardra": {"strength": "strong", "direction": "rising", "risk": "high"},
            "Punarvasu": {"strength": "moderate", "direction": "high", "risk": "medium"},
            "Pushya": {"strength": "strong", "direction": "falling", "risk": "high"},
            "Ashlesha": {"strength": "weak", "direction": "low", "risk": "low"},
            "Magha": {"strength": "strong", "direction": "rising", "risk": "high"},
            "Purva Phalguni": {"strength": "moderate", "direction": "high", "risk": "medium"},
            "Uttara Phalguni": {"strength": "strong", "direction": "falling", "risk": "high"},
            "Hasta": {"strength": "weak", "direction": "low", "risk": "low"},
            "Chitra": {"strength": "strong", "direction": "rising", "risk": "high"},
            "Swati": {"strength": "moderate", "direction": "high", "risk": "medium"},
            "Vishakha": {"strength": "strong", "direction": "falling", "risk": "high"},
            "Anuradha": {"strength": "weak", "direction": "low", "risk": "low"},
            "Jyeshtha": {"strength": "strong", "direction": "rising", "risk": "high"},
            "Mula": {"strength": "moderate", "direction": "high", "risk": "medium"},
            "Purva Ashadha": {"strength": "strong", "direction": "falling", "risk": "high"},
            "Uttara Ashadha": {"strength": "weak", "direction": "low", "risk": "low"},
            "Shravana": {"strength": "strong", "direction": "rising", "risk": "high"},
            "Dhanishta": {"strength": "moderate", "direction": "high", "risk": "medium"},
            "Shatabhisha": {"strength": "strong", "direction": "falling", "risk": "high"},
            "Purva Bhadrapada": {"strength": "weak", "direction": "low", "risk": "low"},
            "Uttara Bhadrapada": {"strength": "strong", "direction": "rising", "risk": "high"},
            "Revati": {"strength": "moderate", "direction": "high", "risk": "medium"}
        }
        
        # Tithi-based amplification
        tithi_amplification = {
            "Purnima": 1.5,      # Full moon - highest tides
            "Amavasya": 1.4,     # New moon - high tides
            "Ekadashi": 1.2,     # Eleventh day - moderate amplification
            "Ashtami": 1.1,      # Eighth day - slight amplification
            "Chaturdashi": 1.3   # Fourteenth day - high amplification
        }
        
        base_tide = nakshatra_tides.get(nakshatra, {"strength": "moderate", "direction": "stable", "risk": "medium"})
        amplification = tithi_amplification.get(tithi, 1.0)
        
        return {
            'nakshatra_tide': base_tide,
            'tithi_amplification': amplification,
            'overall_strength': base_tide['strength'],
            'direction': base_tide['direction'],
            'risk_level': base_tide['risk'],
            'recommendation': self._get_recommendation(base_tide, tithi)
        }
    
    def _get_recommendation(self, tide_info: Dict, tithi: str) -> str:
        """Get recommendation based on tide factors"""
        if tide_info['risk'] == 'high':
            return "High tide alert - monitor coastal areas closely"
        elif tide_info['risk'] == 'medium':
            return "Moderate tides - normal coastal monitoring"
        else:
            return "Low tides - reduced coastal risk"


class TideCalculator:
    """Calculate tide predictions based on astronomical factors"""
    
    def __init__(self, base_height: float = 1.5, tide_range: float = 2.0):
        self.base_height = base_height
        self.tide_range = tide_range
    
    def calculate_tide_height(self, time: datetime, hindu_influence: Dict) -> float:
        """Calculate tide height for given time"""
        # Base astronomical tide (12.42 hour cycle)
        hour_factor = time.hour + time.minute / 60
        astronomical_tide = self.base_height + 0.5 * math.sin(2 * math.pi * hour_factor / 12.42)
        
        # Adjust for Hindu calendar influence
        strength_multiplier = {
            'strong': 1.3,
            'moderate': 1.1,
            'weak': 0.9
        }
        
        strength = hindu_influence['nakshatra_tide']['strength']
        multiplier = strength_multiplier.get(strength, 1.0)
        
        # Apply tithi amplification
        amplification = hindu_influence['tithi_amplification']
        
        # Calculate final height
        final_height = astronomical_tide * multiplier * amplification
        
        # Add some randomness for realism
        random_factor = 0.1 * math.sin(time.hour * 0.5)
        final_height += random_factor
        
        # Ensure reasonable bounds
        return max(0.1, min(5.0, final_height))
    
    def determine_tide_type(self, height: float, time: datetime) -> str:
        """Determine tide type based on height and time"""
        if height > self.base_height + 0.5:
            return 'high'
        elif height < self.base_height - 0.5:
            return 'low'
        elif time.hour % 6 < 3:
            return 'rising'
        else:
            return 'falling'


class WeatherSimulator:
    """Simulate weather conditions for tide correlation"""
    
    def __init__(self):
        self.conditions = ['clear', 'cloudy', 'rainy', 'stormy', 'windy']
    
    def get_weather(self, time: datetime, latitude: float) -> WeatherData:
        """Generate simulated weather data"""
        import random
        
        # Base temperature with daily cycle
        base_temp = 20 + 10 * math.sin(2 * math.pi * time.hour / 24)
        temperature = base_temp + random.uniform(-3, 3)
        
        # Weather condition based on time and randomness
        if random.random() < 0.3:
            condition = 'rainy'
        elif random.random() < 0.5:
            condition = 'cloudy'
        else:
            condition = 'clear'
        
        # Wind speed
        wind_speed = random.uniform(0, 15)
        
        # Humidity
        humidity = random.uniform(40, 80)
        
        return WeatherData(
            timestamp=time,
            temperature=temperature,
            condition=condition,
            wind_speed=wind_speed,
            humidity=humidity
        )


class TidePredictor:
    """Main tide prediction system"""
    
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.hindu_calendar = HinduCalendar()
        self.tide_calculator = TideCalculator()
        self.weather_simulator = WeatherSimulator()
    
    def predict_tides(self, start_date: datetime, days: int = 7) -> List[TidePrediction]:
        """Predict tides for given period"""
        predictions = []
        
        for i in range(days * 24):  # Hourly predictions
            current_time = start_date + timedelta(hours=i)
            
            # Get Hindu calendar influence
            hindu_date = self.hindu_calendar.get_current_hindu_date(current_time)
            tide_influence = self.hindu_calendar.get_tide_influence(hindu_date)
            
            # Calculate tide height
            tide_height = self.tide_calculator.calculate_tide_height(current_time, tide_influence)
            
            # Determine tide type
            tide_type = self.tide_calculator.determine_tide_type(tide_height, current_time)
            
            # Get weather
            weather = self.weather_simulator.get_weather(current_time, self.latitude)
            
            # Create prediction
            prediction = TidePrediction(
                timestamp=current_time,
                height_meters=tide_height,
                tide_type=tide_type,
                confidence=0.85,
                hindu_factors=hindu_date,
                weather_info={
                    'condition': weather.condition,
                    'temperature': f"{weather.temperature:.1f}°C",
                    'wind_speed': f"{weather.wind_speed:.1f} m/s",
                    'humidity': f"{weather.humidity:.0f}%"
                }
            )
            
            predictions.append(prediction)
        
        return predictions
    
    def get_hazard_assessment(self, predictions: List[TidePrediction]) -> Dict[str, Any]:
        """Assess coastal hazards based on predictions"""
        high_risk = []
        moderate_risk = []
        
        for pred in predictions:
            risk_score = 0
            
            # High tide risk
            if pred.tide_type == 'high' and pred.height_meters > 3.0:
                risk_score += 3
            elif pred.tide_type == 'high':
                risk_score += 2
            
            # Weather risk
            if pred.weather_info:
                if pred.weather_info['condition'] == 'stormy':
                    risk_score += 3
                elif pred.weather_info['condition'] == 'rainy':
                    risk_score += 1
                
                wind_speed = float(pred.weather_info['wind_speed'].split()[0])
                if wind_speed > 10:
                    risk_score += 2
            
            # Hindu calendar risk
            if pred.hindu_factors.get('nakshatra') in ['Ashwini', 'Krittika', 'Ardra', 'Pushya', 'Magha', 'Chitra', 'Vishakha', 'Jyeshtha', 'Purva Ashadha', 'Shravana', 'Shatabhisha', 'Purva Bhadrapada']:
                risk_score += 1
            
            # Categorize risk
            if risk_score >= 5:
                high_risk.append({
                    'timestamp': pred.timestamp,
                    'risk_score': risk_score,
                    'tide_height': pred.height_meters,
                    'tide_type': pred.tide_type,
                    'weather': pred.weather_info,
                    'hindu_factors': pred.hindu_factors
                })
            elif risk_score >= 3:
                moderate_risk.append({
                    'timestamp': pred.timestamp,
                    'risk_score': risk_score,
                    'tide_height': pred.height_meters,
                    'tide_type': pred.tide_type,
                    'weather': pred.weather_info,
                    'hindu_factors': pred.hindu_factors
                })
        
        return {
            'high_risk_count': len(high_risk),
            'moderate_risk_count': len(moderate_risk),
            'high_risk_periods': high_risk[:5],
            'moderate_risk_periods': moderate_risk[:5],
            'overall_risk': 'HIGH' if high_risk else 'MODERATE' if moderate_risk else 'LOW'
        }


def main():
    """Main function for testing and demonstration"""
    print("🌊 Tide and Weather Forecasting System with Hindu Calendar")
    print("=" * 60)
    
    # Initialize predictor for San Francisco Bay Area
    predictor = TidePredictor(latitude=37.7749, longitude=-122.4194)
    
    # Predict tides for next 7 days
    start_date = datetime.now()
    print(f"\n📅 Predicting tides from {start_date.strftime('%Y-%m-%d %H:%M')}")
    
    predictions = predictor.predict_tides(start_date, days=7)
    
    if predictions:
        print(f"✅ Generated {len(predictions)} tide predictions")
        
        # Show next 24 hours
        print(f"\n🌊 Next 24 Hours Tide Predictions:")
        print("-" * 90)
        print(f"{'Time':<20} {'Height':<8} {'Type':<10} {'Nakshatra':<15} {'Tithi':<15} {'Weather':<15}")
        print("-" * 90)
        
        for pred in predictions[:24]:
            print(f"{pred.timestamp.strftime('%m-%d %H:%M'):<20} "
                  f"{pred.height_meters:.2f}m{'':<4} "
                  f"{pred.tide_type:<10} "
                  f"{pred.hindu_factors['nakshatra']:<15} "
                  f"{pred.hindu_factors['tithi']:<15} "
                  f"{pred.weather_info['condition']:<15}")
        
        # Show Hindu calendar influence
        print(f"\n🕉️ Hindu Calendar Tide Influence:")
        print("-" * 50)
        first_pred = predictions[0]
        hindu_date = first_pred.hindu_factors
        
        print(f"Current Nakshatra: {hindu_date['nakshatra']}")
        print(f"Current Tithi: {hindu_date['tithi']}")
        print(f"Lunar Fortnight: {hindu_date['paksha']}")
        
        # Get tide influence
        hindu_calendar = HinduCalendar()
        tide_influence = hindu_calendar.get_tide_influence(hindu_date)
        
        print(f"Tide Strength: {tide_influence['overall_strength']}")
        print(f"Tide Direction: {tide_influence['direction']}")
        print(f"Risk Level: {tide_influence['risk_level']}")
        print(f"Recommendation: {tide_influence['recommendation']}")
        
        # Hazard assessment
        print(f"\n🚨 Coastal Hazard Assessment:")
        print("-" * 50)
        hazards = predictor.get_hazard_assessment(predictions)
        
        print(f"Overall Risk: {hazards['overall_risk']}")
        print(f"High Risk Periods: {hazards['high_risk_count']}")
        print(f"Moderate Risk Periods: {hazards['moderate_risk_count']}")
        
        if hazards['high_risk_periods']:
            print(f"\n⚠️ High Risk Periods:")
            for period in hazards['high_risk_periods'][:3]:
                print(f"  {period['timestamp'].strftime('%m-%d %H:%M')} "
                      f"(Risk Score: {period['risk_score']})")
        
        # Save predictions
        output_file = "tide_predictions.json"
        try:
            # Convert to serializable format
            serializable_predictions = []
            for pred in predictions:
                serializable_pred = {
                    'timestamp': pred.timestamp.isoformat(),
                    'height_meters': pred.height_meters,
                    'tide_type': pred.tide_type,
                    'confidence': pred.confidence,
                    'hindu_factors': pred.hindu_factors,
                    'weather_info': pred.weather_info
                }
                serializable_predictions.append(serializable_pred)
            
            with open(output_file, 'w') as f:
                json.dump({
                    'location': {'latitude': predictor.latitude, 'longitude': predictor.longitude},
                    'predictions': serializable_predictions,
                    'hazards': hazards
                }, f, indent=2)
            
            print(f"\n💾 Predictions saved to {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving predictions: {e}")
    
    else:
        print("❌ Failed to generate tide predictions")


if __name__ == "__main__":
    main()
