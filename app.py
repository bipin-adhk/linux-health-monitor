
from flask import Flask, jsonify, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import psutil

app = Flask(__name__)

# Define measurements Prometheus can collect
cpu_gauge = Gauge(
    "health_cpu_percent",
    "CPU usage percentage"
)

memory_gauge = Gauge(
    "health_memory_percent",
    "Memory usage percentage"
)

disk_gauge = Gauge(
    "health_disk_percent",
    "Disk usage percentage"
)


@app.route("/")
def home():
    return jsonify({
        "application": "Linux Health Monitor",
        "status": "running"
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


def read_system_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent
    }


@app.route("/metrics")
def metrics():
    return jsonify(read_system_metrics())


@app.route("/prometheus")
def prometheus_metrics():
    data = read_system_metrics()

    cpu_gauge.set(data["cpu_percent"])
    memory_gauge.set(data["memory_percent"])
    disk_gauge.set(data["disk_percent"])

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
