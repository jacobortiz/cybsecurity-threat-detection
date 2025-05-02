# Threat Detection Data Generator

This module generates simulated network and system logs with injected malicious indicators for training and testing threat detection systems.

## Features

- **Network Logs**: Generates Zeek-like connection logs in CSV format
  - Includes source/destination IPs, ports, protocols, and traffic statistics
  - 10% of generated logs contain malicious indicators
  - Simulates connections to known bad IPs

- **System Logs**: Generates RFC-5424 compliant syslog entries
  - Includes proper facility and severity levels
  - Simulates both normal system activity and suspicious events
  - 10% of generated logs contain malicious indicators

- **Malware Events**: Generates JSONL-formatted malware activity logs
  - Simulates process creation, file access, and registry changes
  - Includes realistic malicious process names and commands

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the generator:
```bash
python generator.py
```

This will generate:
- `network_logs/connections.csv`: Network connection logs
- `system_logs/syslog.txt`: System activity logs
- `malware_events/events.jsonl`: Malware activity logs

## Customization

You can modify the generator by:
- Adjusting the `num_records` parameter in `generate_sample_data()`
- Adding more malicious IPs in `NetworkLogGenerator.bad_ips`
- Adding more malicious processes in `MalwareEventGenerator.malicious_processes`
- Adding more suspicious commands in `MalwareEventGenerator.suspicious_commands`

## Output Formats

### Network Logs (CSV)
```csv
ts,uid,id.orig_h,id.orig_p,id.resp_h,id.resp_p,proto,service,duration,orig_bytes,resp_bytes,label
2023-05-02T11:00:00Z,C1,10.0.0.5,12345,93.184.216.34,80,tcp,http,30.5,5000,300,benign
```

### System Logs (Text)
```
<34>May  2 11:01:05 host1 sudo: 'su root' failed for user on /dev/pts/0
<13>May  2 11:02:10 host2 sshd[1234]: Invalid user admin from 10.0.0.20 port 34567
```

### Malware Events (JSONL)
```json
{"timestamp": "2023-05-02T11:04:00Z", "host": "host3", "event_type": "process_create", "process_name": "BadWare.exe", "params": "--encrypt"}
``` 