# Threat Detection Processor

The Threat Detection Processor is a microservice that processes security logs in real-time, analyzes them for potential threats using machine learning, and generates alerts when suspicious activities are detected.

## Features

- Real-time log processing from multiple sources:
  - Zeek network logs
  - Syslog entries
  - Phishing URL access logs
- Structured log parsing and validation
- Machine learning-based threat detection
- Real-time alert generation
- Redis-based message queue integration

## Architecture

The processor service is part of a larger threat detection system and works as follows:

1. **Log Ingestion**: Consumes logs from Redis pub/sub channel 'logs'
2. **Log Parsing**: Parses different log formats into structured events
3. **Feature Extraction**: Extracts relevant features for ML prediction
4. **Threat Detection**: Sends features to ML API for prediction
5. **Alert Generation**: Publishes alerts to Redis channel 'alerts' when threats are detected

## Prerequisites

- Docker and Docker Compose
- Redis server
- ML API service (for threat predictions, in ml-api folder)

## Configuration

The processor service can be configured using environment variables:

- `REDIS_HOST`: Redis server hostname (default: 'redis')
- `REDIS_PORT`: Redis server port (default: 6379)
- `ML_API_URL`: ML API service URL (default for this project: 'http://ml-api:5000')

## Log Formats (Examples, generated)

### Zeek Network Logs
```
ts,uid,id.orig_h,id.orig_p,id.resp_h,id.resp_p,proto,service,duration,orig_bytes,resp_bytes,label
2025-05-02T11:00:00Z,C1,10.0.0.5,12345,93.184.216.34,80,tcp,http,30.5,5000,300,benign
```

### Syslog Entries
```
<34>May  2 11:01:05 host1 sudo: 'su root' failed for user on /dev/pts/0
```

### Phishing URL Logs
```
2025-05-02T11:03:00Z,client=10.0.0.5,url=http://malicious.example.com/login.php,action=blocked
```

## Alert Format

Alerts are published to Redis channel 'alerts' in JSON format:

```json
{
    "timestamp": "2025-05-06T18:36:37.022Z",
    "event_type": "phishing_url",
    "threat_type": "phishing",
    "confidence": 0.95,
    "details": {
        "client": "10.0.0.5",
        "url": "http://malicious.example.com/login.php",
        "action": "blocked"
    }
}
```

## Development

### Project Structure
```
processor/
├── Dockerfile
├── README.md
├── requirements.txt
├── main.py          # Main processor service
└── log_parser.py    # Log parsing utilities
```

### Adding New Log Types

To add support for a new log type:

1. Add a new parser method in `log_parser.py`
2. Update the `_parse_log` method in `main.py` to handle the new format
3. Add feature extraction logic in `_extract_features` method

## Testing

To test the processor:

1. Start the services:
```bash
docker-compose up
```

2. Publish a test log to Redis:
```bash
redis-cli publish logs "2025-05-02T11:03:00Z,client=10.0.0.5,url=http://malicious.example.com/login.php,action=blocked"
```

or if running redis on docker
```bash
docker exec cs-threat-detector-redis-1 redis-cli publish logs "2025-05-02T11:03:00Z,client=10.0.0.5,url=http://malicious.example.com/login.php,action=blocked"
```

3. Check for alerts:
```bash
redis-cli subscribe alerts
```

```bash
docker exec cs-threat-detector-redis-1 redis-cli subsribe alerts
```


## Tests

Zeek network log

```bash
docker exec cs-threat-detector-redis-1 redis-cli publish logs "ts,uid,id.orig_h,id.orig_p,id.resp_h,id.resp_p,proto,service,duration,orig_bytes,resp_bytes,label\n2025-05-02T11:00:00Z,C1,10.0.0.5,12345,93.184.216.34,80,tcp,http,30.5,5000,300,benign"
```

Syslog with failed password

```bash
docker exec cs-threat-detector-redis-1 redis-cli publish logs '<34>May 06 19:45:23 webserver sshd[12345]: Failed password for root from 192.168.1.100 port 22'
```

Phishing URL log with malicious URL

```bash
docker exec cs-threat-detector-redis-1 redis-cli publish logs '2025-05-02T11:03:00Z,client=10.0.0.5,url=http://malicious.example.com/login.php,action=blocked'
```

## Note
currently gives mock predictions

## License

MIT