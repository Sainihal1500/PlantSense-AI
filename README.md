# PlantSense AI

## Overview

PlantSense AI is a **real‑time plant health monitoring dashboard** that visualises biometric sensor data (moisture, temperature, humidity, bio‑signal) and provides AI‑driven health status, issue detection, and actionable recommendations.

The project consists of:
- A **Flask backend** (`app.py`) that serves the dashboard and a `/get-data` endpoint.
- An **optional Express mock server** (`server.js`) that can simulate sensor data for Node‑only environments.
- A **frontend dashboard** (`templates/index-2.html`) built with vanilla HTML/CSS/JS and Chart.js.
- A **serial‑reading service** (`read_serial.py`) for real hardware integration.

The application can run in **demo mode** (no hardware required) or connect to actual sensors via a serial port.

---

## Features

- Live telemetry visualisation with Chart.js (moisture, temperature, humidity, bio‑signal).
- AI‑generated health status, issue list, and advice.
- Manual sensor input for testing.
- Secure HTTP headers and CSP.
- Configurable via environment variables.
- Optional Node.js mock server for lightweight simulation.

---

## Prerequisites

- **macOS** (tested on macOS 14).
- **Python ≥3.12** (the code runs on 3.14 in the test environment).
- **Node.js** (optional, only if you wish to run the mock server).
- **FFmpeg** – required by Hyperframes for video generation (already installed).
- **Chrome/Chromium headless** – used by Hyperframes for rendering.

---

## Installation

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/Sainihal1500/PlantSense-AI.git
cd PlantSense-AI

# Create a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

If you plan to use the optional Express server:

```bash
npm install   # will install Express (see package.json)
```

---

## Configuration

Copy the example environment file and adjust values as needed:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `HOST` | Flask bind address | `127.0.0.1` |
| `PORT` | Flask port | `5001` |
| `FLASK_DEBUG` | Enable Flask debug mode (`1`/`0`) | `0` |
| `CORS_ORIGIN` | Allowed CORS origin (`*` for any) | `*` |
| `DEMO_MODE` | Use simulated data (`1`/`0`) | `1` |
| `SERIAL_PORT` | Serial device path (e.g., `/dev/cu.usbserial-XYZ`) | *empty* |
| `SERIAL_BAUD` | Baud rate for serial communication | `9600` |
| `SERIAL_TIMEOUT` | Serial read timeout (seconds) | `1.0` |
| `API_URL` | Front‑end base URL for the Flask backend (used by the dashboard) | `http://127.0.0.1:5001` |

---

## Running the Application

### Flask backend (primary)

```bash
source .venv/bin/activate   # ensure the venv is active
python3 app.py
```

The dashboard will be available at `http://127.0.0.1:5001/`.

### Optional Express mock server

```bash
npm start   # runs server.js on port 3000 by default
```

You can point the frontend to this server by setting `API_URL` accordingly.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the dashboard HTML. |
| `/health` | GET | Liveness probe – returns JSON with service status. |
| `/get-data` | GET | Returns telemetry JSON. In demo mode returns static values; otherwise reads from serial hardware. |

---

## Demo Mode

When `DEMO_MODE=1` (the default) the backend returns a fixed, realistic dataset, allowing you to explore the UI without any hardware.

---

## Hardware Setup (optional)

1. Connect an Arduino or compatible microcontroller that streams comma‑separated `key:value` pairs (e.g. `moisture:65.2,temperature:24.1,humidity:58.0,signal:1.15`).
2. Set `SERIAL_PORT` in `.env` to the device path (use `ls /dev/cu.*` to list).
3. Turn off `DEMO_MODE` (`DEMO_MODE=0`).
4. Restart the Flask server.

---

## Testing & Validation

```bash
# Verify the Flask server starts
python3 -m flask run

# Quick health check
curl http://127.0.0.1:5001/health

# Retrieve telemetry
curl http://127.0.0.1:5001/get-data
```

The dashboard can be opened in a browser; open the developer console to verify there are no CSP or CORS errors.

---

## Security Considerations

- The backend sets a strict Content‑Security‑Policy and other security headers.
- Input fields are validated on the client side; server‑side validation is minimal because data is only visualised.
- **Do not expose real serial device paths or credentials** in the repository; use `.env` (ignored via `.gitignore`).
- Running in production should disable `FLASK_DEBUG` and restrict `CORS_ORIGIN` to the actual domain.

---

## Troubleshooting

- **Missing Flask module** – ensure you have activated the virtual environment and installed `requirements.txt`.
- **Port already in use** – check with `lsof -i :5001` and stop any conflicting process.
- **Serial connection fails** – verify the correct device path and that the user has permission to access it (`chmod` or add to `dialout` group).
- **Chart.js not loading** – the CSP permits `cdn.jsdelivr.net`; ensure no network restrictions block it.

---

## License

This project is provided for educational purposes. Review the individual library licenses (Flask, Express, Chart.js, etc.) for compliance.
