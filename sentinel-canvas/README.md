# Sentinel Canvas

An optional drag-and-drop dashboard builder for [Log Sentinel](../log-sentinel/README.md).

Build your own security dashboard by picking widgets and arranging them exactly how you want — no coding required.

---

## What It Does

- Drag widgets from the sidebar onto the canvas
- Resize and reposition them freely
- Each widget pulls live data from the Log Sentinel API
- Save your layout as a JSON file and reload it anytime
- Completely optional — Log Sentinel works fine without it

## Available Widgets

| Widget | Data Source |
|---|---|
| Stats Counters | `/api/stats` |
| Alert Table | `/api/alerts` |
| Attack Type Chart | `/api/stats` |
| Top Attacking IPs | `/api/stats` |
| Risk Score Timeline | `/api/stats` |
| Incident Panel | `/api/incidents` |

## Requirements

- Python 3.8+
- Log Sentinel's `Dashboard-server.py` must be running (provides the API)
- No extra Python packages needed

## Setup

1. Make sure Log Sentinel is running:
   ```
   # In log-sentinel/
   python sentinel.py
   python Dashboard-server.py
   ```

2. In a new terminal, start Sentinel Canvas:
   ```
   # In sentinel-canvas/
   python canvas-server.py
   ```

3. Open http://localhost:8889 in your browser

## Usage

- **Add a widget** — click any widget in the left sidebar
- **Move a widget** — drag it by its title bar
- **Resize a widget** — drag the bottom-right corner handle
- **Remove a widget** — click the × button on the widget
- **Save layout** — click "Save Layout" to download a `layout.json` file
- **Load layout** — click "Load Layout" and select a previously saved JSON file
- **Refresh data** — widgets auto-refresh every 30 seconds, or click the ↺ button

## Configuration

Edit `canvas-server.py` to change:
- `HOST` — default `localhost`
- `PORT` — default `8889`

The Sentinel API URL (default `http://localhost:8888`) can be changed inside the canvas UI via the settings panel.

## Architecture Note

Sentinel Canvas is intentionally thin — the server only serves one HTML file. All data fetching happens in the browser directly against the Sentinel API. This keeps it lightweight and consistent with the main project's philosophy.
