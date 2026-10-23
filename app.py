"""
PlantSense AI - Core Flask Backend
Serves the real-time biometric plant monitoring dashboard and telemetry endpoints.
"""

import os
import logging
from flask import Flask, jsonify, render_template

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("plantsense-app")

app = Flask(__name__)

# Security & runtime configuration via environment variables
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5001))
DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("true", "1")
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")
DEMO_MODE = os.getenv("DEMO_MODE", "1").lower() in ("true", "1")
SERIAL_PORT = os.getenv("SERIAL_PORT", "")

@app.after_request
def set_security_headers(response):
    """Apply defense-in-depth HTTP security headers."""
    response.headers["Access-Control-Allow-Origin"] = CORS_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    # Content Security Policy (permits self, inline UI assets, and trusted Chart.js CDN)
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self' http://127.0.0.1:* http://localhost:*; "
        "font-src 'self' data:;"
    )
    response.headers["Content-Security-Policy"] = csp
    return response

@app.route('/')
@app.route('/index.html')
@app.route('/index-2.html')
def home():
    """Serve the primary PlantSense AI dashboard template."""
    return render_template('index-2.html')

@app.route('/health')
def health():
    """Liveness & health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "PlantSense AI",
        "version": "1.0.0",
        "demo_mode": DEMO_MODE
    }), 200

@app.route('/get-data')
def get_data():
    """
    Return real-time or simulated biometric sensor telemetry.
    Matches exact keys expected by the frontend: moisture, temperature, humidity, bio_signal.
    """
    # If live serial hardware is enabled and configured, attempt reading
    if not DEMO_MODE and SERIAL_PORT:
        try:
            from read_serial import read_serial_sensor
            data = read_serial_sensor(SERIAL_PORT)
            if data:
                return jsonify({
                    "moisture": round(float(data.get("moisture", 0)), 1),
                    "temperature": round(float(data.get("temperature", 0)), 1),
                    "humidity": round(float(data.get("humidity", 0)), 1),
                    "bio_signal": round(float(data.get("bio_signal", data.get("signal", 0))), 2),
                    "source": "hardware"
                })
        except Exception as e:
            logger.warning("Hardware serial read failed, falling back to baseline demo telemetry: %s", e)

    # Standard verified baseline demo telemetry
    return jsonify({
        "moisture": 65.0,
        "temperature": 30.0,
        "humidity": 60.0,
        "bio_signal": 1.20,
        "source": "demo"
    })

@app.route('/favicon.ico')
def favicon():
    """Handle browser favicon request cleanly without 404 logs."""
    return ('', 204)

if __name__ == "__main__":
    logger.info("Starting PlantSense AI on http://%s:%d (debug=%s, demo_mode=%s)", HOST, PORT, DEBUG, DEMO_MODE)
    app.run(host=HOST, port=PORT, debug=DEBUG)
