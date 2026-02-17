#!/usr/bin/env python3
"""
Log Sentinel Dashboard Server
Serves the dashboard and provides API endpoints to read alerts.log
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler


ALERTS_LOG = 'alerts.log'
HOST = 'localhost'
PORT = 8888


def parse_alerts():
    """Parse alerts.log into structured data"""
    alerts = []

    if not os.path.exists(ALERTS_LOG):
        return alerts

    with open(ALERTS_LOG, 'r') as f:
        content = f.read()

    # Split on separator lines
    blocks = content.split('=' * 80)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        alert = {}

        # Timestamp and type
        match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (.+?) - (CRITICAL|WARNING)', block)
        if match:
            alert['time'] = match.group(1)
            alert['type'] = match.group(2)
            alert['severity'] = match.group(3)
        else:
            continue

        # IP
        ip_match = re.search(r'IP: (.+)', block)
        if ip_match:
            alert['ip'] = ip_match.group(1).strip()

        # Pattern
        pattern_match = re.search(r'Pattern: (.+)', block)
        if pattern_match:
            alert['pattern'] = pattern_match.group(1).strip()

        # Path
        path_match = re.search(r'Path: (.+)', block)
        if path_match:
            alert['path'] = path_match.group(1).strip()

        # User-Agent
        ua_match = re.search(r'User-Agent: (.+)', block)
        if ua_match:
            alert['useragent'] = ua_match.group(1).strip()

        # Requests (rate limit)
        req_match = re.search(r'Requests: (\d+) in (\d+)s', block)
        if req_match:
            alert['requests'] = req_match.group(1)
            alert['window'] = req_match.group(2)

        # 404 count
        count_match = re.search(r'404 Count: (\d+)', block)
        if count_match:
            alert['count'] = count_match.group(1)

        alerts.append(alert)

    return alerts


def build_stats(alerts):
    """Build summary statistics from alerts"""
    if not alerts:
        return {
            'total': 0,
            'critical': 0,
            'warning': 0,
            'top_ips': [],
            'attack_types': [],
            'timeline': []
        }

    critical = sum(1 for a in alerts if a.get('severity') == 'CRITICAL')
    warning = sum(1 for a in alerts if a.get('severity') == 'WARNING')

    # Top attacking IPs
    ip_counts = defaultdict(int)
    for a in alerts:
        if 'ip' in a:
            ip_counts[a['ip']] += 1
    top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Attack type breakdown
    type_counts = defaultdict(int)
    for a in alerts:
        if 'type' in a:
            type_counts[a['type']] += 1
    attack_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

    # Timeline - group by hour
    hour_counts = defaultdict(int)
    for a in alerts:
        if 'time' in a:
            try:
                hour = a['time'][:13]  # YYYY-MM-DD HH
                hour_counts[hour] += 1
            except Exception:
                pass
    timeline = sorted(hour_counts.items())[-24:]  # last 24 hours

    return {
        'total': len(alerts),
        'critical': critical,
        'warning': warning,
        'top_ips': [{'ip': ip, 'count': count} for ip, count in top_ips],
        'attack_types': [{'type': t, 'count': count} for t, count in attack_types],
        'timeline': [{'hour': h, 'count': count} for h, count in timeline]
    }


class DashboardHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/alerts':
            self.serve_alerts()
        elif self.path == '/api/stats':
            self.serve_stats()
        else:
            self.send_response(404)
            self.end_headers()

    def serve_dashboard(self):
        dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
        with open(dashboard_path, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(content)

    def serve_alerts(self):
        alerts = parse_alerts()
        alerts.reverse()  # newest first
        data = json.dumps(alerts[-100:])  # last 100
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data.encode())

    def serve_stats(self):
        alerts = parse_alerts()
        stats = build_stats(alerts)
        data = json.dumps(stats)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data.encode())

    def log_message(self, format, *args):
        pass  # suppress request logs


if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), DashboardHandler)
    print(f"Log Sentinel Dashboard running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
