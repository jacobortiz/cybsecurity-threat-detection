# cybsecurity-threat-detection

## Data ingestion layer
Zeek/Snort/Suricata sensors for network traffic; agents (syslog-ng, NXLog) for system logs

## Stream processing layer
Kafka (or Kinsesis) pipes data; stream processors (Flink/Spark) execute ML inference

## Analytics Engine (ML/Correlation)
runs classifiers and anomaly detectors on each event

## Storage
fast time series DB for metrics/alerts, search index for logs (Elasticsearch)

## Frontend
Next.js?

# AI-Enhanced Malware & Phishing Threat Detector

## Architecture and Components
The system is built as loosely-coupled microservices (each in its own Docker container) connected by a lightweight message broker. A high-level flow is:

Data Generator: Emits mock logs (network Zeek-style logs, syslog entries, phishing URL events, malware actions) into a broker or file.

Message Broker: A simple pub/sub (e.g. Redis) or in-memory queue that buffers log events for processing.

Processor Service: Subscribes to logs, parses each event (extracts fields like timestamps, URLs, process names), calls the ML API for classification, and publishes any alerts.
ML API: A Python Flask (or FastAPI) microservice that loads a pre-trained model and returns “threat”/“benign” predictions. Tutorials show how to save a trained classifier and expose it via Flask for real-time inference.

Frontend Dashboard: A Next.js app that fetches alerts (e.g. via REST or by tailing an alerts log) and displays them in a table plus charts. Chart.js (or Plotly) is used to render threat trends; e.g. Chart.js’s docs demonstrate building charts from data sets.

Figure: MVP Architecture – simulated logs → pipeline → ML API → alerts → Dashboard. 

Each service runs in Docker. For example, the ML API container might run Flask with scikit-learn/XGBoost, Processor runs a Python script with Redis client, Generator runs a Python script, Frontend runs Node/Next.js, and Redis runs from the official Redis image. They communicate over a user-defined Docker network. Persistent volumes (or bind mounts) can expose log folders (e.g. /logs) between services for inspection and future persistence.

Simulated Data Generation
I mimic both network logs and host logs, with injected phishing/malware indicators.

### Network Traffic Logs (Zeek-like): 
I generate synthetic Zeek connection logs (e.g. CSV or JSON conn.log entries) and DNS/HTTP logs. Each record can include fields like timestamp, source/dest IP, ports, protocol, bytes, etc. Zeek (formerly Bro) naturally produces such logs for all flows. For example, the IoT-23 dataset uses Zeek to label each connection as malicious or benign. Our generator can simply output lines like:
```
ts, uid, id.orig_h, id.orig_p, id.resp_h, id.resp_p, proto, service, duration, orig_bytes, resp_bytes, label
2025-05-02T11:00:00Z,C1,10.0.0.5,12345,93.184.216.34,80,tcp,http,30.5,5000,300,benign
```
Include occasional “malware” flows (e.g. connections to known bad IPs or long-duration data transfers).

### System (Syslog) Logs: 
Simulate host/system logs in RFC-5424 or RFC-3164 format. Each line includes a priority, timestamp, hostname, service/process, and message. For instance:

```
<34>May  2 11:01:05 host1 sudo: 'su root' failed for user on /dev/pts/0
<13>May  2 11:02:10 host2 sshd[1234]: Invalid user admin from 10.0.0.20 port 34567
```

(Here <34> encodes facility/severity, as per syslog specs). We embed phishing or malware clues in these logs: e.g. a user clicking a phishing link logged by an HTTP proxy, or an antivirus alert line.

### Phishing URLs & Malware Behaviors: 
I include test cases, e.g.:
Phishing URLs: A small CSV of URLs labeled phishing/benign (e.g. from Kaggle or PhishTank). The generator can simulate a web proxy log entry when a phishing URL is accessed. For example: 2025-05-02T11:03:00Z,client=10.0.0.5, url=http://malicious.example.com/login.php, action=blocked. One can use publicly available URL features (domain age, presence of '@', etc.) as model inputs. Studies show ML can achieve ~96% accuracy on such URL datasets.

Malware Events: Fake process logs or file events. For instance, a log line like 2025-05-02T11:04:00Z,host=host3,event=process_create,program=BadWare.exe,params="--encrypt", or registry changes proc=cmd.exe, cmd="reg add ... suspicious". These illustrate typical malware actions. I tag some as “malware” events in training/testing.
I keep data simple but structured. The logs may be written to files or streamed via sockets. Key is having enough fields for the ML model (e.g. URL string or tokens, or process names) and ground-truth labels for testing.


## ML Classifier Component
A lightweight classifier distinguishes benign vs. malicious events (phishing or malware). For example, using Python’s scikit-learn or XGBoost.

### Training Data: 
Collect or synthesize labeled examples. For phishing, one can use a Kaggle URL dataset (e.g. ~11,430 URLs, half phishing) with engineered features (URL length, number of dots, presence of suspicious words). This reference shows XGBoost gave ~96.6% accuracy on such data. For malware, one could use the IoT-23 flows (with labels) or generate synthetic events labeled as attack/normal.

### Features: 
Extract numeric and categorical features. (E.g. for URLs: presence of “@”, count of subdomains, domain reputation; for network flows: packet counts, unusual ports; for host logs: process name blacklists, command patterns.)

### Model: 
Train a simple classifier (XGBoost or even logistic regression). Using scikit-learn: split data into train/test, fit the model, and pickle the trained model. Save the model to disk (e.g. model.pkl).

### Serving:
Flask (FastAPI)

To test the ML component independently, run the training script on open data (e.g. the Kaggle phishing dataset or any CSV of labeled URLs) and verify accuracy. Documenting this training process (data source, feature list) is important but kept minimal here.


## Processing Pipeling
Simple pipeline to flow log data through parsing and ML, then generate alerts.

Broker: Run a Redis container and use Python’s redis-py to publish/subscribe. Logs from the generator are pushed to a Redis channel (e.g. logs). Alternatively, a Python queue or even a filesystem tail loop could be used, but Redis is a common lightweight broker.

Ingestion Script: A Python log producer script reads our synthetic log files (or generates events on the fly) and publishes each line/event to Redis. This simulates continuous log ingestion.

Consumer & Parser: Another Python service subscribes to the same Redis channel. For each incoming log event, it parses the structured fields (splitting Zeek CSV, extracting syslog parts, etc.). It then prepares the feature vector for ML.
Model Invocation: The parser calls the ML API (HTTP request to Flask) with event data. If the model predicts a threat (e.g. phishing or malware), the processor constructs an alert.

Alert Routing: Alerts can be published to another channel or written to a file/DB. For MVP simplicity, the processor could append alerts to a JSON file or send them via WebSocket to the UI. Each alert might include timestamp, type (phish/malware), and details (e.g. URL or process name).

## Frontend
Next.js
Data Fetching: The UI can pull alerts via an API endpoint (e.g. the processor could expose recent alerts at /api/alerts) or directly read from a shared JSON file or message broker. In Next.js, an API route (pages/api) could proxy to Redis or file.

Table View: Display each alert (timestamp, type, description) in a sortable table. For minimal setup, hard-code column names and map over alert list.

Chart/Trend: Use Chart.js (via a React wrapper or a simple component) to visualize alert counts over time.
Design: Keep the UI basic (e.g. plain Bootstrap or simple CSS)


## Docker Deployment
Docker Compose to launch all services


## Local Setup
-----