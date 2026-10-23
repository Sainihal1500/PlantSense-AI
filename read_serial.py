"""
PlantSense AI - Hardware Serial Telemetry Reader
Reads biometric micro-voltage and soil telemetry from connected microcontroller/Arduino.
Gracefully handles missing hardware, timeouts, and malformed serial data.
"""

import os
import logging
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("plantsense-serial")

app = Flask(__name__)

# Configurable environment settings
DEFAULT_PORT = "/dev/cu.usbserial-1140"
SERIAL_PORT = os.getenv("SERIAL_PORT", DEFAULT_PORT)
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", 9600))
SERIAL_TIMEOUT = float(os.getenv("SERIAL_TIMEOUT", 1.0))
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5002))
DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("true", "1")

# Lazy-loaded serial connection object
_serial_conn = None

def get_serial_connection(port=None, baud=None, timeout=None):
    """
    Safely initialize or retrieve the serial connection.
    Returns None if serial hardware or pyserial library is unavailable.
    """
    global _serial_conn
    try:
        import serial
    except ImportError:
        logger.warning("pyserial is not installed. Install with: pip install pyserial")
        return None

    target_port = port or SERIAL_PORT
    target_baud = baud or SERIAL_BAUD
    target_timeout = timeout or SERIAL_TIMEOUT

    # Reuse existing connection if open
    if _serial_conn is not None and getattr(_serial_conn, "is_open", False):
        return _serial_conn

    try:
        _serial_conn = serial.Serial(target_port, target_baud, timeout=target_timeout)
        logger.info("Successfully connected to serial device on %s (%d baud)", target_port, target_baud)
        return _serial_conn
    except Exception as e:
        logger.warning("Could not open serial device %s: %s", target_port, e)
        _serial_conn = None
        return None

def parse_serial_line(line_str):
    """
    Safely parse key:value comma-delimited serial output.
    Example input: 'moisture:65.2,temperature:24.1,humidity:58.0,signal:1.15'
    """
    if not line_str or not isinstance(line_str, str):
        return None
    data = {}
    try:
        parts = line_str.strip().split(',')
        for p in parts:
            if ':' in p:
                k, v = p.split(':', 1)
                k = k.strip().lower()
                data[k] = float(v.strip())
        return data if data else None
    except Exception as e:
        logger.debug("Failed to parse serial line '%s': %s", line_str, e)
        return None

def read_serial_sensor(port=None):
    """
    Read and parse a single telemetry line from the serial device.
    Returns parsed dictionary or None.
    """
    ser = get_serial_connection(port=port)
    if not ser:
        return None
    try:
        raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
        return parse_serial_line(raw_line)
    except Exception as e:
        logger.warning("Error reading line from serial port: %s", e)
        return None

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def home():
    return jsonify({
        "service": "PlantSense AI Serial Gateway",
        "configured_port": SERIAL_PORT,
        "status": "online"
    })

@app.route('/get-data')
def get_data():
    """Endpoint serving real-time telemetry from hardware, with clean fallback."""
    data = read_serial_sensor()
    if data:
        return jsonify({
            "moisture": round(float(data.get("moisture", 0)), 1),
            "temperature": round(float(data.get("temperature", 0)), 1),
            "humidity": round(float(data.get("humidity", 0)), 1),
            "bio_signal": round(float(data.get("signal", data.get("bio_signal", 0))), 2),
            "source": "hardware"
        })
    else:
        # Fallback when hardware is not connected
        return jsonify({
            "moisture": 0.0,
            "temperature": 0.0,
            "humidity": 0.0,
            "bio_signal": 0.0,
            "source": "hardware_offline",
            "message": "Hardware disconnected or awaiting sensor signal"
        })

if __name__ == "__main__":
    logger.info("Starting Serial Service on http://%s:%d (device=%s)", HOST, PORT, SERIAL_PORT)
    app.run(host=HOST, port=PORT, debug=DEBUG)
