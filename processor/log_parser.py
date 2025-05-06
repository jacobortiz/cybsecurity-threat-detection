from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel
import csv
import re
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class LogEvent:
    event_type: str
    timestamp: datetime
    parsed_data: Dict[str, Any]

class LogParser:
    def parse_zeek_log(self, log_line: str) -> Optional[LogEvent]:
        """Parse Zeek network log format."""
        try:
            logger.info(f"Parsing Zeek log: {log_line}")
            # Split fields (expecting: ts,uid,id.orig_h,id.orig_p,id.resp_h,id.resp_p,proto,service,duration,orig_bytes,resp_bytes,label)
            fields = log_line.strip().split(',')
            logger.info(f"Split into {len(fields)} fields: {fields}")
            
            if len(fields) != 12:
                logger.warning(f"Expected 12 fields, got {len(fields)}")
                return None
                
            # Parse timestamp
            timestamp = datetime.fromisoformat(fields[0].replace('Z', '+00:00'))
            logger.info(f"Parsed timestamp: {timestamp}")
            
            # Extract relevant fields
            parsed_data = {
                'protocol': fields[6],
                'service': fields[7],
                'duration': float(fields[8]),
                'orig_bytes': int(fields[9]),
                'resp_bytes': int(fields[10]),
                'label': fields[11]
            }
            logger.info(f"Parsed data: {parsed_data}")
            
            return LogEvent(
                event_type='zeek_conn',
                timestamp=timestamp,
                parsed_data=parsed_data
            )
        except Exception as e:
            logger.error(f"Error parsing Zeek log: {e}")
            return None
            
    def parse_syslog(self, log_line: str) -> Optional[LogEvent]:
        """Parse syslog format."""
        try:
            # Basic syslog format: <PRI>TIMESTAMP HOSTNAME PROGRAM[PID]: MESSAGE
            pattern = r'<(\d+)>(\w{3}\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\S+)(?:\[(\d+)\])?:\s+(.*)'
            match = re.match(pattern, log_line)
            
            if not match:
                return None
                
            priority, timestamp_str, hostname, program, pid, message = match.groups()
            
            # Parse timestamp (assuming current year)
            current_year = datetime.now().year
            timestamp = datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
            
            parsed_data = {
                'priority': int(priority),
                'hostname': hostname,
                'program': program,
                'pid': int(pid) if pid else None,
                'message': message
            }
            
            return LogEvent(
                event_type='syslog',
                timestamp=timestamp,
                parsed_data=parsed_data
            )
        except Exception as e:
            print(f"Error parsing syslog: {e}")
            return None
            
    def parse_phishing_log(self, log_line: str) -> Optional[LogEvent]:
        """Parse phishing URL log format."""
        try:
            # Format: timestamp,client=IP,url=URL,action=ACTION
            parts = log_line.strip().split(',')
            if len(parts) != 4:
                return None
                
            timestamp = datetime.fromisoformat(parts[0].replace('Z', '+00:00'))
            
            # Parse key-value pairs
            client = parts[1].split('=')[1]
            url = parts[2].split('=')[1]
            action = parts[3].split('=')[1]
            
            parsed_data = {
                'client': client,
                'url': url,
                'action': action
            }
            
            return LogEvent(
                event_type='phishing_url',
                timestamp=timestamp,
                parsed_data=parsed_data
            )
        except Exception as e:
            print(f"Error parsing phishing log: {e}")
            return None 