# Linux Health Monitor | Prometheus, Grafana & Node Exporter

A practical Linux monitoring project built using Docker Compose, Python Flask, Prometheus, Node Exporter, and Grafana.

The project monitors application availability and Linux system resources, including CPU, RAM, and disk usage. It also generates alerts and sends email notifications when monitoring conditions are triggered.

## Project Overview

The project was completed in two phases.

**Phase 1: Application Monitoring**

Built a Python Flask application and used Prometheus to monitor its availability. Grafana was configured to visualize application health and send email alerts when the application stopped responding or recovered.

**Phase 2: Linux Infrastructure Monitoring**

Extended the existing Docker Compose environment by adding Node Exporter to collect system-level metrics from Kali Linux.

Prometheus collects the metrics, while Grafana displays CPU, memory, and disk utilization through a custom dashboard.

Additional alert rules detect high resource usage, low disk space, and Node Exporter availability failures.

## Technologies Used

- Linux (Kali Linux)
- Docker and Docker Compose
- Python Flask
- Prometheus
- Node Exporter
- Grafana
- PromQL
- Grafana Alerting and SMTP email notifications

## Monitoring Architecture

```text
               Kali Linux
                   |
         +---------+---------+
         |                   |
    Flask Application    Node Exporter
    (Application)        (CPU, RAM, Disk)
         |                   |
         +---------+---------+
                   |
               Prometheus
           (Metrics Collection)
                   |
                Grafana
          (Dashboards & Alerts)
                   |
             Email Notification
              (SMTP / Gmail)
```

## Features

**Application Monitoring**
- Monitor Flask application availability.
- Detect when the application becomes unavailable.
- Send firing and resolved email notifications.

**Infrastructure Monitoring**
- Monitor Linux CPU utilization.
- Monitor RAM usage and available memory.
- Monitor disk utilization.
- Track Node Exporter availability.

**Grafana Dashboard**
- CPU usage over time.
- RAM usage over time.
- Disk utilization.
- Node Exporter availability status.

## PromQL Queries

### CPU Usage (%)

```promql
100 * (1 - avg(rate(node_cpu_seconds_total{job="node-exporter",mode="idle"}[5m])))
```

### RAM Usage (%)

```promql
100 * (1 - node_memory_MemAvailable_bytes{job="node-exporter"} / node_memory_MemTotal_bytes{job="node-exporter"})
```

### Disk Usage (%)

```promql
100 * (1 - node_filesystem_avail_bytes{job="node-exporter",mountpoint="/",device="/dev/sda1"} / node_filesystem_size_bytes{job="node-exporter",mountpoint="/",device="/dev/sda1"})
```

The disk device is specific to this Kali Linux environment and may differ on another machine.

### Node Exporter Availability

```promql
up{job="node-exporter"}
```

- `1` means Prometheus can scrape Node Exporter.
- `0` means Prometheus cannot scrape Node Exporter.

## Alert Configuration

| Alert | Condition | Pending Duration |
|---|---|---|
| High CPU Usage | CPU above 85% | 5 minutes |
| High RAM Usage | RAM above 85% | 5 minutes |
| Low Disk Space | Available space below 15% | 5 minutes |
| Node Exporter Down | `up` below 1 | 1 minute |
| Flask Application Down | Application unavailable | Configured in Phase 1 |

## Testing and Results

### Phase 1: Application Availability

The Flask application was intentionally stopped to verify the availability alert. Grafana successfully generated firing and recovery notifications.

### Phase 2: CPU Alert

The CPU alert threshold was temporarily lowered to safely simulate an alert condition.

Results:
- Grafana detected the condition.
- The alert transitioned to Firing.
- An email notification was successfully delivered.
- The original alert threshold was restored.
- Grafana sent a resolved notification.

### Node Exporter Failure Simulation

Node Exporter was intentionally stopped using Docker Compose.

Results:
- Prometheus reported `up = 0`.
- Grafana triggered the Node Exporter Down alert.
- The firing email was successfully received.
- Node Exporter was restarted.
- Prometheus subsequently reported `up = 1`.

### Container Restart Verification

The Docker Compose stack was restarted successfully.

All four services restarted:
- health-monitor
- prometheus
- node-exporter
- grafana

The Grafana monitoring dashboard remained available after restarting the containers.

The RAM and disk alert rules were configured and observed in their Normal states. Their firing notifications were not separately tested.

## Running the Project

Clone the repository and enter the project directory.

```bash
git clone <https://github.com/bipin-adhk/linux-health-monitor>
cd linux-health-monitor
```

Configure the required environment variables locally using a `.env` file:

```env
GMAIL_USER=your-email@example.com
GMAIL_APP_PASSWORD=your-app-password
```

Use a Gmail app password where supported, not your regular account password. Do not commit the `.env` file.

Start the monitoring stack:

```bash
docker compose up -d --build
```

Access the services:

| Service | URL |
|---|---|
| Flask Application | http://127.0.0.1:5000 |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3000 |

Node Exporter is accessed internally by Prometheus at `node-exporter:9100`.

The provided Node Exporter configuration is designed for a Linux Docker host. Host filesystem access and filesystem device names may need adjustment on other systems.

## Security Considerations

- Application dashboards are bound to localhost for this lab.
- Node Exporter is not published directly to the host network.
- Email credentials are supplied through environment variables.
- Secrets and `.env` files must be excluded from version control.
- Production deployments should use pinned image versions, appropriate authentication, and restricted access.

## What I Learned

This project helped me understand how application and infrastructure monitoring work together.

I gained practical experience collecting Linux system metrics, writing PromQL queries, building Grafana dashboards, configuring alert thresholds, and verifying email notifications through controlled failure simulations.

The project also demonstrated why monitoring infrastructure needs its own availability checks.

## Future Improvements

- Add network traffic monitoring.
- Monitor additional Linux hosts.
- Add disk I/O and container-specific metrics.
- Export Grafana dashboards and alert configurations for reproducible deployment.
- Add security log monitoring and correlation with infrastructure metrics.

## Conclusion

This project demonstrates a practical monitoring environment where application failures, resource utilization, and monitoring-agent availability can be observed through dashboards and alert notifications.

It provides hands-on experience with infrastructure monitoring, troubleshooting, incident detection, and operational reliability.
