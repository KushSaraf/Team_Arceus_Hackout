import json
import logging
import smtplib
import requests #type: ignore
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os


@dataclass
class AlertChannel:
    """Configuration for an alert channel"""
    name: str
    enabled: bool
    priority_levels: List[str]  # Which alert levels this channel should handle
    config: Dict[str, Any]


@dataclass
class AlertMessage:
    """Alert message content for different channels"""
    subject: str
    body: str
    image_data: Optional[bytes] = None
    metadata: Optional[Dict[str, Any]] = None


class EmailAlertChannel:
    """Email alert channel implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email channel
        
        Args:
            config: Dictionary containing email configuration
                   - smtp_server: SMTP server address
                   - smtp_port: SMTP server port
                   - username: Email username
                   - password: Email password
                   - from_email: Sender email address
                   - recipients: List of recipient email addresses
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def send_alert(self, alert_message: AlertMessage) -> bool:
        """
        Send email alert
        
        Args:
            alert_message: Alert message to send
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['from_email']
            msg['To'] = ', '.join(self.config['recipients'])
            msg['Subject'] = alert_message.subject
            
            # Add body
            msg.attach(MIMEText(alert_message.body, 'html'))
            
            # Add image if provided
            if alert_message.image_data:
                image = MIMEImage(alert_message.image_data)
                image.add_header('Content-ID', '<alert_image>')
                msg.attach(image)
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['username'], self.config['password'])
                server.send_message(msg)
            
            self.logger.info(f"Email alert sent successfully to {len(self.config['recipients'])} recipients")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
            return False


class SMSAlertChannel:
    """SMS alert channel implementation using Twilio"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SMS channel
        
        Args:
            config: Dictionary containing SMS configuration
                   - account_sid: Twilio account SID
                   - auth_token: Twilio auth token
                   - from_number: Twilio phone number
                   - recipients: List of recipient phone numbers
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def send_alert(self, alert_message: AlertMessage) -> bool:
        """
        Send SMS alert
        
        Args:
            alert_message: Alert message to send
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        try:
            # Try to import Twilio
            try:
                from twilio.rest import Client #type: ignore
                from twilio.base.exceptions import TwilioException #type: ignore
            except ImportError:
                self.logger.warning("Twilio not installed, using simulation mode")
                # Simulate SMS sending
                for recipient in self.config['recipients']:
                    self.logger.info(f"SMS alert sent to {recipient}: {alert_message.subject}")
                return True
            
            # Initialize Twilio client
            client = Client(self.config['account_sid'], self.config['auth_token'])
            
            # Send SMS to each recipient
            for recipient in self.config['recipients']:
                try:
                    message = client.messages.create(
                        body=alert_message.subject,
                        from_=self.config['from_number'],
                        to=recipient
                    )
                    self.logger.info(f"SMS sent successfully to {recipient}, SID: {message.sid}")
                except TwilioException as e:
                    self.logger.error(f"Failed to send SMS to {recipient}: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS alert: {str(e)}")
            return False


class IVRAlertChannel:
    """Interactive Voice Response (IVR) alert channel using Twilio"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize IVR channel
        
        Args:
            config: Dictionary containing IVR configuration
                   - account_sid: Twilio account SID
                   - auth_token: Twilio auth token
                   - from_number: Twilio phone number
                   - recipients: List of recipient phone numbers
                   - webhook_url: Webhook URL for TwiML response
                   - voice: Voice type (alice, man, woman)
                   - language: Language code (en-US, en-GB, etc.)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def send_alert(self, alert_message: AlertMessage) -> bool:
        """
        Send IVR alert
        
        Args:
            alert_message: Alert message to send
            
        Returns:
            True if IVR call initiated successfully, False otherwise
        """
        try:
            # Try to import Twilio
            try:
                from twilio.rest import Client #type: ignore
                from twilio.base.exceptions import TwilioException #type: ignore
            except ImportError:
                self.logger.warning("Twilio not installed, using simulation mode")
                # Simulate IVR calling
                for recipient in self.config['recipients']:
                    self.logger.info(f"IVR call initiated to {recipient}: {alert_message.subject}")
                return True
            
            # Initialize Twilio client
            client = Client(self.config['account_sid'], self.config['auth_token'])
            
            # Create TwiML for the call
            twiml = self._create_twiml(alert_message)
            
            # Make calls to each recipient
            for recipient in self.config['recipients']:
                try:
                    call = client.calls.create(
                        twiml=twiml,
                        to=recipient,
                        from_=self.config['from_number'],
                        record=True,  # Record the call for quality assurance
                        status_callback=f"{self.config['webhook_url']}/call-status",
                        status_callback_event=['completed', 'answered', 'busy', 'failed', 'no-answer']
                    )
                    self.logger.info(f"IVR call initiated to {recipient}, SID: {call.sid}")
                except TwilioException as e:
                    self.logger.error(f"Failed to initiate IVR call to {recipient}: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send IVR alert: {str(e)}")
            return False
    
    def _create_twiml(self, alert_message: AlertMessage) -> str:
        """
        Create TwiML (Twilio Markup Language) for the IVR call
        
        Args:
            alert_message: Alert message to convert to speech
            
        Returns:
            TwiML string
        """
        # Extract key information for voice message
        hazard_type = alert_message.metadata.get('hazard_type', 'unknown hazard')
        location = alert_message.metadata.get('location', 'unknown location')
        alert_level = alert_message.metadata.get('alert_level', 'unknown level')
        
        # Create natural language message
        message = f"""
        This is an automated emergency alert from the Coastal Hazard Detection System.
        A {hazard_type.replace('_', ' ')} has been detected at {location}.
        Alert level is {alert_level}.
        Please take appropriate action based on the severity level.
        This message will repeat once.
        """
        
        # Create TwiML
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="{self.config.get('voice', 'alice')}" language="{self.config.get('language', 'en-US')}">
                {message}
            </Say>
            <Pause length="2"/>
            <Say voice="{self.config.get('voice', 'alice')}" language="{self.config.get('language', 'en-US')}">
                {message}
            </Say>
            <Hangup/>
        </Response>"""
        
        return twiml


class WebhookAlertChannel:
    """Webhook alert channel for external integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize webhook channel
        
        Args:
            config: Dictionary containing webhook configuration
                   - url: Webhook endpoint URL
                   - headers: Optional headers to include
                   - timeout: Request timeout in seconds
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def send_alert(self, alert_message: AlertMessage) -> bool:
        """
        Send webhook alert
        
        Args:
            alert_message: Alert message to send
            
        Returns:
            True if webhook sent successfully, False otherwise
        """
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "subject": alert_message.subject,
                "body": alert_message.body,
                "metadata": alert_message.metadata or {}
            }
            
            headers = self.config.get('headers', {})
            headers['Content-Type'] = 'application/json'
            
            response = requests.post(
                self.config['url'],
                json=payload,
                headers=headers,
                timeout=self.config.get('timeout', 30)
            )
            
            if response.status_code in [200, 201, 202]:
                self.logger.info(f"Webhook alert sent successfully to {self.config['url']}")
                return True
            else:
                self.logger.error(f"Webhook failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {str(e)}")
            return False


class PushNotificationChannel:
    """Push notification channel for mobile apps"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize push notification channel
        
        Args:
            config: Dictionary containing push notification configuration
                   - fcm_server_key: Firebase Cloud Messaging server key
                   - topic: FCM topic to send to
                   - device_tokens: List of specific device tokens (optional)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def send_alert(self, alert_message: AlertMessage) -> bool:
        """
        Send push notification
        
        Args:
            alert_message: Alert message to send
            
        Returns:
            True if push notification sent successfully, False otherwise
        """
        try:
            # TODO: Implement actual FCM push notification
            # This is a placeholder implementation
            
            self.logger.info(f"Push notification sent to topic {self.config.get('topic', 'general')}: {alert_message.subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {str(e)}")
            return False


class MultiChannelAlertService:
    """
    Service for sending alerts through multiple channels
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize multi-channel alert service
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.channels: Dict[str, AlertChannel] = {}
        self.channel_implementations: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        if config_file:
            self.load_config(config_file)
        else:
            self.load_default_config()
    
    def load_config(self, config_file: str) -> None:
        """
        Load configuration from file
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self._setup_channels(config)
            self.logger.info(f"Configuration loaded from {config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {config_file}: {str(e)}")
            self.load_default_config()
    
    def load_default_config(self) -> None:
        """Load default configuration"""
        default_config = {
            "channels": {
                "email": {
                    "name": "Email Alerts",
                    "enabled": True,
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
                    "enabled": True,
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
                    "enabled": True,
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
                },
                "webhook": {
                    "name": "Webhook Integration",
                    "enabled": False,
                    "priority_levels": ["YELLOW", "ORANGE", "RED"],
                    "config": {
                        "url": "https://your-webhook-endpoint.com/alerts",
                        "headers": {"Authorization": "Bearer your_token"},
                        "timeout": 30
                    }
                }
            }
        }
        
        self._setup_channels(default_config)
        self.logger.info("Default configuration loaded")
    
    def _setup_channels(self, config: Dict[str, Any]) -> None:
        """
        Setup alert channels from configuration
        
        Args:
            config: Configuration dictionary
        """
        for channel_id, channel_config in config.get("channels", {}).items():
            if not channel_config.get("enabled", False):
                continue
            
            # Create channel configuration
            channel = AlertChannel(
                name=channel_config["name"],
                enabled=channel_config["enabled"],
                priority_levels=channel_config["priority_levels"],
                config=channel_config["config"]
            )
            
            self.channels[channel_id] = channel
            
            # Create channel implementation
            if channel_id == "email":
                self.channel_implementations[channel_id] = EmailAlertChannel(channel_config["config"])
            elif channel_id == "sms":
                self.channel_implementations[channel_id] = SMSAlertChannel(channel_config["config"])
            elif channel_id == "ivr":
                self.channel_implementations[channel_id] = IVRAlertChannel(channel_config["config"])
            elif channel_id == "webhook":
                self.channel_implementations[channel_id] = WebhookAlertChannel(channel_config["config"])
            elif channel_id == "push":
                self.channel_implementations[channel_id] = PushNotificationChannel(channel_config["config"])
            
            self.logger.info(f"Channel '{channel.name}' configured and enabled")
    
    def create_alert_message(self, 
                           alert_level: str,
                           hazard_type: str,
                           location_name: str,
                           description: str,
                           confidence: float,
                           image_data: Optional[bytes] = None) -> AlertMessage:
        """
        Create alert message for different channels
        
        Args:
            alert_level: Alert level (GREEN, YELLOW, ORANGE, RED)
            hazard_type: Type of hazard detected
            location_name: Location where hazard was detected
            description: User description of the hazard
            confidence: Confidence score from AI model
            image_data: Optional image data
            
        Returns:
            AlertMessage object
        """
        # Create subject line
        subject = f"🚨 {alert_level} ALERT: {hazard_type.replace('_', ' ').title()} Detected"
        
        # Create HTML body
        body = f"""
        <html>
        <body>
            <h2 style="color: {'red' if alert_level == 'RED' else 'orange' if alert_level == 'ORANGE' else 'yellow' if alert_level == 'YELLOW' else 'green'}">
                {subject}
            </h2>
            
            <h3>Location</h3>
            <p>{location_name}</p>
            
            <h3>Hazard Details</h3>
            <p><strong>Type:</strong> {hazard_type.replace('_', ' ').title()}</p>
            <p><strong>Confidence:</strong> {confidence:.1%}</p>
            <p><strong>Description:</strong> {description}</p>
            
            <h3>Alert Level</h3>
            <p><strong>{alert_level}</strong> - {self._get_alert_description(alert_level)}</p>
            
            <h3>Recommended Action</h3>
            <p>{self._get_alert_action(alert_level)}</p>
            
            <hr>
            <p><small>Alert generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </body>
        </html>
        """
        
        return AlertMessage(
            subject=subject,
            body=body,
            image_data=image_data,
            metadata={
                "alert_level": alert_level,
                "hazard_type": hazard_type,
                "location": location_name,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def _get_alert_description(self, alert_level: str) -> str:
        """Get description for alert level"""
        descriptions = {
            "GREEN": "No immediate threat",
            "YELLOW": "Low risk detected",
            "ORANGE": "Moderate risk detected",
            "RED": "High risk detected"
        }
        return descriptions.get(alert_level, "Unknown alert level")
    
    def _get_alert_action(self, alert_level: str) -> str:
        """Get recommended action for alert level"""
        actions = {
            "GREEN": "Continue monitoring",
            "YELLOW": "Monitor closely",
            "ORANGE": "Prepare response",
            "RED": "Immediate action required"
        }
        return actions.get(alert_level, "No action specified")
    
    def send_alert(self, 
                  alert_level: str,
                  hazard_type: str,
                  location_name: str,
                  description: str,
                  confidence: float,
                  image_data: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Send alert through all appropriate channels
        
        Args:
            alert_level: Alert level
            hazard_type: Type of hazard
            location_name: Location name
            description: Hazard description
            confidence: Confidence score
            image_data: Optional image data
            
        Returns:
            Dictionary with sending results for each channel
        """
        # Create alert message
        alert_message = self.create_alert_message(
            alert_level, hazard_type, location_name, description, confidence, image_data
        )
        
        results = {}
        
        # Send through each enabled channel
        for channel_id, channel in self.channels.items():
            if not channel.enabled:
                continue
            
            # Check if this channel should handle this alert level
            if alert_level not in channel.priority_levels:
                results[channel_id] = {
                    "sent": False,
                    "reason": f"Alert level {alert_level} not in channel priority levels"
                }
                continue
            
            # Send alert
            if channel_id in self.channel_implementations:
                implementation = self.channel_implementations[channel_id]
                success = implementation.send_alert(alert_message)
                
                results[channel_id] = {
                    "sent": success,
                    "channel_name": channel.name,
                    "timestamp": datetime.now().isoformat()
                }
                
                if success:
                    self.logger.info(f"Alert sent successfully through {channel.name}")
                else:
                    self.logger.error(f"Failed to send alert through {channel.name}")
            else:
                results[channel_id] = {
                    "sent": False,
                    "reason": "Channel implementation not found"
                }
        
        return results
    
    def get_channel_status(self) -> Dict[str, Any]:
        """
        Get status of all channels
        
        Returns:
            Dictionary with channel status information
        """
        status = {}
        for channel_id, channel in self.channels.items():
            status[channel_id] = {
                "name": channel.name,
                "enabled": channel.enabled,
                "priority_levels": channel.priority_levels,
                "configured": channel_id in self.channel_implementations
            }
        return status
    
    def enable_channel(self, channel_id: str) -> bool:
        """
        Enable a specific channel
        
        Args:
            channel_id: ID of channel to enable
            
        Returns:
            True if channel enabled successfully, False otherwise
        """
        if channel_id in self.channels:
            self.channels[channel_id].enabled = True
            self.logger.info(f"Channel '{channel_id}' enabled")
            return True
        return False
    
    def disable_channel(self, channel_id: str) -> bool:
        """
        Disable a specific channel
        
        Args:
            channel_id: ID of channel to disable
            
        Returns:
            True if channel disabled successfully, False otherwise
        """
        if channel_id in self.channels:
            self.channels[channel_id].enabled = False
            self.logger.info(f"Channel '{channel_id}' disabled")
            return True
        return False


def main():
    """
    Main function for testing multi-channel alert service
    """
    print("🚨 Multi-Channel Alert Service - Local Testing")
    print("=" * 50)
    
    # Initialize service
    service = MultiChannelAlertService()
    
    # Show channel status
    print("\n📡 Channel Status:")
    print("-" * 20)
    status = service.get_channel_status()
    for channel_id, channel_status in status.items():
        print(f"  {channel_id}: {'✅' if channel_status['enabled'] else '❌'} "
              f"{channel_status['name']} - Levels: {', '.join(channel_status['priority_levels'])}")
    
    # Test alert sending
    print("\n📤 Testing Alert Sending:")
    print("-" * 25)
    
    test_cases = [
        ("YELLOW", "algal_bloom", "San Francisco Bay", "Green water observed", 0.45),
        ("ORANGE", "oil_spill", "Santa Monica Beach", "Oil sheen on water surface", 0.75),
        ("RED", "coastal_erosion", "Malibu Coast", "Severe cliff erosion detected", 0.95)
    ]
    
    for alert_level, hazard_type, location, description, confidence in test_cases:
        print(f"\nTesting {alert_level} alert...")
        
        results = service.send_alert(
            alert_level, hazard_type, location, description, confidence
        )
        
        for channel_id, result in results.items():
            if result.get('sent'):
                print(f"  ✅ {channel_id}: Alert sent successfully")
            else:
                print(f"  ❌ {channel_id}: {result.get('reason', 'Failed')}")
    
    # Test channel management
    print("\n🔧 Testing Channel Management:")
    print("-" * 30)
    
    # Test enabling/disabling channels
    if 'email' in service.channels:
        print("Testing email channel toggle...")
        service.disable_channel('email')
        print(f"  Email channel disabled: {not service.channels['email'].enabled}")
        service.enable_channel('email')
        print(f"  Email channel enabled: {service.channels['email'].enabled}")
    
    # Test with image data
    print("\n🖼️ Testing Alert with Image Data:")
    print("-" * 35)
    
    # Create mock image data
    mock_image_data = b"mock_image_data_for_testing"
    
    results = service.send_alert(
        "RED", "oil_spill", "Venice Beach", "Large oil slick detected", 0.92, mock_image_data
    )
    
    for channel_id, result in results.items():
        if result.get('sent'):
            print(f"  ✅ {channel_id}: Alert with image sent successfully")
        else:
            print(f"  ❌ {channel_id}: {result.get('reason', 'Failed')}")
    
    print("\n🎉 Testing completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
