# Behavioral Threat Hunting - Log Sentinel

Log Sentinel is a lightweight, real-time log monitor for Nginx-style access logs. It detects common web attacks using pattern rules, rate limiting, and 404 spam heuristics, and can optionally serve a live dashboard for alerts and stats.

## Features
- Detects SQL injection, XSS, path traversal, and command injection
- Flags known scanner User-Agents
- Rate limit and 404 spam detection per IP
- Console alerts and file-based alert logging
- Optional dashboard with API endpoints

## Project Structure
- log-sentinel/
  - sentinel.py: Log monitor and detection engine
  - config.yaml: Runtime settings
  - Dashboard-server.py: Dashboard HTTP server
  - dashboard.html: Dashboard UI
  - rules/: Pattern files for detection
  - test.sh: Log attack simulator (bash)

## Requirements
- Python 3.8+
- PyYAML

## Setup
1) Create a virtual environment (optional) and install dependencies:

```bash
pip install pyyaml
```

2) Update the log path and settings in log-sentinel/config.yaml if needed.

## Run the Sentinel
From the log-sentinel directory:

```bash
python sentinel.py
```

The sentinel tails the configured log file and writes alerts to alerts.log.

## Run the Dashboard
In a separate terminal, from log-sentinel:

```bash
python Dashboard-server.py
```

Then open http://localhost:8888 in a browser.

## Simulate Attacks
The test script appends sample attack lines to the configured log.

```bash
bash test.sh
```

Note: On Windows, run this in Git Bash or WSL.

## Configuration
Key settings in log-sentinel/config.yaml:
- log_file: Path to access log to monitor
- alert_log: Output file for alerts
- enable_*_detection: Toggle detectors
- rate_limit_*: Rate limit settings
- enable_404_detection / max_404_per_minute
- whitelist_ips: Comma-separated IPs to skip

## Rules
Detection patterns live in log-sentinel/rules/:
- sqli_patterns.txt
- xss_patterns.txt
- traversal_patterns.txt
- cmdi_patterns.txt
- scanner_patterns.txt

Patterns are treated as case-insensitive regular expressions.

## Output
Alerts are written to alerts.log and optionally printed to the console. The dashboard reads alerts.log and exposes:
- GET /api/alerts (last 100 alerts)
- GET /api/stats (summary stats)

## Notes
- The Nginx log regex expects the default combined log format.
- alert levels are labeled INFO/WARNING/CRITICAL but the minimum level filter is not enforced in code yet.
