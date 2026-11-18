# Linux Health Monitor

A hands-on observability lab built with **Python Flask**, **Docker Compose**, **Prometheus**, and **Grafana**. The project demonstrates how to monitor an application's availability, detect an outage, notify an operator by email, and verify recovery.

## What this project does

- Runs a lightweight Flask health-monitoring application in Docker.
- Uses Prometheus to scrape the application's metrics endpoint.
- Visualizes monitoring data in Grafana.
- Detects a failed Prometheus scrape using the `up` metric.
- Sends **FIRING** and **RESOLVED** email notifications through Grafana using Gmail SMTP.
- Demonstrates a full application outage and recovery test.

## Architecture

```text
                 Docker Compose
+------------------------------------------------+
|                                                |
|  Flask application (health-monitor:5000)        |
|              |                                 |
|              | metrics scrape                  |
|              v                                 |
|  Prometheus (prometheus:9090)                   |
|              |                                 |
|              | PromQL query                    |
|              v                                 |
|  Grafana (grafana:3000)                         |
|              |                                 |
|              | alert rule: up < 1              |
+--------------|---------------------------------+
               |
               v
      Gmail SMTP notification
       FIRING / RESOLVED
```

## Technology stack

| Technology | Purpose |
| --- | --- |
| Python / Flask | Health-monitor application |
| Docker / Docker Compose | Container orchestration for the lab |
| Prometheus | Metrics scraping and availability checking |
| Grafana | Dashboarding and alert evaluation |
| Gmail SMTP | Email delivery for alert and recovery notifications |

## Repository layout

```text
linux-health-monitor/
├── app.py
├── compose.yaml
├── Dockerfile
├── prometheus/
│   └── prometheus.yml
├── requirements.txt
├── README.md
└── .gitignore
```

> Local-only files such as `.env`, `compose.yaml.backup`, and any app-password files must **not** be committed. The `.env` file contains SMTP credentials and is intentionally absent from the repository.

## Running the lab

**Prerequisites:** Docker Engine and the Docker Compose plugin.

```bash
git clone <YOUR_REPOSITORY_URL>
cd linux-health-monitor
docker compose up -d
docker compose ps
```

On the machine running Docker, visit:

| Component | Local URL |
| --- | --- |
| Flask application | http://127.0.0.1:5000 |
| Prometheus | http://127.0.0.1:9090 |
| Grafana | http://127.0.0.1:3000 |

The Flask root endpoint returns a JSON health response such as:

```json
{
  "application": "Linux Health Monitor",
  "status": "running"
}
```

**Note:** Gmail alerting requires an additional, private SMTP configuration described below. The application and monitoring stack can be explored without configuring email first if `compose.yaml` supports running without SMTP credentials.

## Prometheus monitoring

In Prometheus, query the configured Flask scrape job:

```promql
up{job="linux-health-monitor"}
```

- `1`: Prometheus successfully scraped the monitored endpoint.
- `0`: Prometheus failed to scrape the endpoint.

This metric measures scrape reachability, **not** complete application health or user-facing uptime.

## Grafana application-down alert

The Grafana-managed alert used for this lab is named **Health-monitor-flask Down**.

| Setting | Value |
| --- | --- |
| Data source | Prometheus |
| Query | `up{job="linux-health-monitor"}` |
| Query type | Instant |
| Alert condition | Is below `1` |
| Evaluation | Tested at 10-second intervals |
| Contact point | Email contact point configured in Grafana |

When the metric becomes `0`, the condition becomes true and Grafana can enter the **Firing** state. After the Flask application recovers and Prometheus reports `1`, the alert returns to **Normal**.

## Reproduce the outage and recovery

1. Confirm the stack is up:

   ```bash
   docker compose ps
   ```

2. Simulate an outage by stopping only the Flask service:

   ```bash
   docker compose stop health-monitor
   ```

3. In Prometheus, check that `up{job="linux-health-monitor"}` eventually becomes `0`.
4. In Grafana, verify that **Health-monitor-flask Down** enters **Firing** and a FIRING email arrives (if SMTP is configured).
5. Restore the service:

   ```bash
   docker compose start health-monitor
   ```

6. Verify that the metric returns to `1`, Grafana returns to **Normal**, and a RESOLVED email arrives.

Notification timing may be affected by alert evaluation, grouping, SMTP delivery, and system resource constraints.

## Gmail notifications (keep credentials private)

Grafana can send email through Gmail SMTP using an eligible Google account and an **App Password**. Enable two-step verification and create an App Password in your Google account where supported.

Keep a local `.env` file outside Git:

```dotenv
GMAIL_USER=your-address@gmail.com
GMAIL_APP_PASSWORD=your-google-app-password
```

The Grafana service in `compose.yaml` may use environment-variable substitution:

```yaml
environment:
  GF_SMTP_ENABLED: "true"
  GF_SMTP_HOST: "smtp.gmail.com:587"
  GF_SMTP_USER: "${GMAIL_USER}"
  GF_SMTP_PASSWORD: "${GMAIL_APP_PASSWORD}"
  GF_SMTP_FROM_ADDRESS: "${GMAIL_USER}"
  GF_SMTP_FROM_NAME: "Linux Health Monitor"
  GF_SMTP_STARTTLS_POLICY: "MandatoryStartTLS"
```

Add `.env` to `.gitignore` and restrict its permissions with `chmod 600 .env`. Do not commit real App Passwords, credentials, SMTP logs with secrets, or unredacted personal email screenshots. If a credential has ever been committed, **revoke/rotate it**; `.gitignore` does not remove it from Git history.

In Grafana, create an Email contact point and assign it to the application-down alert. Ensure **Disable resolved message** is unchecked to receive recovery notifications.

## Evidence from the lab

The lab was validated by observing:

1. Flask returning `"status": "running"` from the local application endpoint.
2. Prometheus `up` changing from `1` to `0` during the outage.
3. Grafana displaying the application-down alert in **Firing**.
4. A **[FIRING]** email arriving in Gmail.
5. The alert returning to **Normal** after the container was restarted.
6. A **[RESOLVED]** email arriving in Gmail.

Screenshots may be added under `docs/screenshots/` after removing personal email addresses and other private information.

## Key lessons

- Metrics collection, visualization, and alerting are different functions.
- A dashboard displays current and historical observations; an alert evaluates a condition without constant manual monitoring.
- Prometheus `up` is useful for scrape availability checks.
- An incident workflow includes detection, notification, response, and recovery verification.
- Monitoring credentials should be kept out of version control.

## Future improvements

- Add Node Exporter for CPU, memory, and disk metrics.
- Add resource usage alerts and tune pending periods to reduce alert noise.
- Provision Grafana dashboards and alert rules as code for reproducible deployments.
- Add more meaningful application health and request-level metrics.

## Scope

This is an educational home lab, not a production monitoring deployment. The exact alert evaluation and delivery times depend on local settings and system performance.
