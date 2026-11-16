
from flask import Flask, jsonify
import psutil

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "application": "Linux Health Monitor",
        "status": "running"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/metrics")
def metrics():
    return jsonify({
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

