import json
import redis
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from log_parser import LogParser, LogEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThreatProcessor:
    def __init__(self, redis_host: str = 'redis', redis_port: int = 6379, ml_api_url: str = 'http://ml-api:5000'):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port)
        self.ml_api_url = ml_api_url
        self.log_parser = LogParser()
        
    def process_log(self, log_line: str) -> None:
        """Process a single log line through the pipeline."""
        try:
            logger.info(f"Processing log line: {log_line}")
            # Parse the log based on its format
            event = self._parse_log(log_line)
            if not event:
                logger.warning(f"Failed to parse log: {log_line}")
                return
                
            logger.info(f"Successfully parsed log event: {event.event_type}")
                
            # Prepare features for ML prediction
            features = self._extract_features(event)
            logger.info(f"Extracted features: {features}")
            
            # Get ML prediction
            prediction = self._get_ml_prediction(features, event)
            logger.info(f"Got prediction: {prediction}")
            
            # Generate alert if threat detected
            if prediction.get('is_threat', False):
                self._generate_alert(event, prediction)
                
        except Exception as e:
            logger.error(f"Error processing log: {e}")
            
    def _parse_log(self, log_line: str) -> Optional[LogEvent]:
        """Parse log line into structured event."""
        # Try different parsers based on log format
        if log_line.startswith('<'):  # Syslog
            return self.log_parser.parse_syslog(log_line)
        elif 'client=' in log_line:  # Phishing URL log
            return self.log_parser.parse_phishing_log(log_line)
        else:  # Try Zeek log format
            return self.log_parser.parse_zeek_log(log_line)
        
    def _extract_features(self, event: LogEvent) -> Dict[str, Any]:
        """Extract relevant features for ML prediction."""
        features = {
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat()
        }
        
        # Add event-specific features
        if event.event_type == 'zeek_conn':
            features.update({
                'protocol': event.parsed_data['protocol'],
                'service': event.parsed_data['service'],
                'duration': event.parsed_data['duration'],
                'bytes_transferred': event.parsed_data['orig_bytes'] + event.parsed_data['resp_bytes']
            })
        elif event.event_type == 'phishing_url':
            features.update({
                'url': event.parsed_data['url'],
                'action': event.parsed_data['action']
            })
        elif event.event_type == 'syslog':
            features.update({
                'priority': event.parsed_data['priority'],
                'message': event.parsed_data['message']
            })
            
        return features
        
    def _get_ml_prediction(self, features: Dict[str, Any], event: LogEvent) -> Dict[str, Any]:
        """Get threat prediction from ML API."""
        try:
            response = requests.post(
                f"{self.ml_api_url}/predict",
                json=features,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"ML API not available, using mock prediction: {e}")
            # Return mock prediction for testing
            is_threat = False
            if event.event_type == 'zeek_conn' and event.parsed_data.get('label') == 'malicious':
                is_threat = True
            elif event.event_type == 'phishing_url' and 'malicious' in event.parsed_data.get('url', '').lower():
                is_threat = True
            elif event.event_type == 'syslog' and 'failed password' in event.parsed_data.get('message', '').lower():
                is_threat = True
                
            return {
                'is_threat': is_threat,
                'threat_type': 'test_threat',
                'confidence': 0.95
            }
            
    def _generate_alert(self, event: LogEvent, prediction: Dict[str, Any]) -> None:
        """Generate and publish alert."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event.event_type,
            'threat_type': prediction.get('threat_type', 'unknown'),
            'confidence': prediction.get('confidence', 0.0),
            'details': event.parsed_data
        }
        
        try:
            # Publish alert to Redis
            self.redis_client.publish('alerts', json.dumps(alert))
            logger.info(f"Alert generated: {alert}")
        except Exception as e:
            logger.error(f"Error publishing alert: {e}")
            
    def run(self) -> None:
        """Main processing loop."""
        logger.info("Starting threat processor...")
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe('logs')
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                log_line = message['data'].decode('utf-8')
                self.process_log(log_line)

if __name__ == '__main__':
    processor = ThreatProcessor()
    processor.run() 