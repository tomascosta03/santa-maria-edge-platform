# Santa Maria Edge Platform

A resilient Edge-to-Cloud IoT telemetry platform designed for environments with intermittent connectivity.

The project simulates a distributed IoT infrastructure capable of collecting telemetry from remote devices, processing data locally at the edge, and synchronizing with the cloud once connectivity is restored.

It is being developed as a practical study of Distributed Systems, IoT, Cloud Computing, Observability and Resilient Software Architectures.

---

## Motivation

Many IoT deployments operate in locations where cloud connectivity cannot be assumed.

Examples include:

- Islands
- Industrial facilities
- Ships
- Offshore platforms
- Remote scientific stations

In these environments, sensors must continue operating even when the cloud becomes temporarily unavailable.

Traditional cloud-first architectures often assume continuous connectivity, which may lead to:

- Data loss
- Unavailable services
- Duplicated messages
- Inconsistent system state

This project explores an alternative architecture where the Edge node becomes the primary execution environment while the Cloud acts as a synchronization and long-term processing layer.

---

## Objectives

The platform should:

- Collect telemetry from multiple simulated IoT devices
- Process telemetry locally
- Validate incoming data
- Detect anomalous measurements
- Store telemetry on the Edge
- Continue operating without cloud connectivity
- Synchronize pending data once connectivity returns
- Prevent duplicate message processing
- Expose operational metrics
- Demonstrate production-oriented engineering practices

---

## High-Level Architecture

The platform is divided into two logical environments:

- **Edge**, responsible for collecting, validating and temporarily storing telemetry.
- **Cloud**, responsible for long-term storage, centralized processing and future analytics.

```text
                          EDGE

+------------------------+
| Simulated IoT Devices  |
+-----------+------------+
            |
            | MQTT
            ▼
+------------------------+
| Eclipse Mosquitto      |
+-----------+------------+
            |
            ▼
+------------------------+
| Edge Ingestion Service |
+-----------+------------+
            |
     +------+------+
     |             |
     ▼             ▼
+-----------+   +------------------+
| PostgreSQL|   | Synchronization  |
|   Edge    |   | Queue            |
+-----------+   +--------+---------+
                         |
                         | Internet
                         ▼

                         CLOUD

+------------------------+
| FastAPI Cloud API      |
+-----------+------------+
            |
            ▼
+------------------------+
| PostgreSQL Cloud       |
+------------------------+

Monitoring

Prometheus
Grafana
OpenTelemetry
```

---

## Technology Stack

| Layer | Technology |
|--------|------------|
| Language | Python |
| Messaging | MQTT |
| Broker | Eclipse Mosquitto |
| API | FastAPI |
| Database | PostgreSQL |
| Containers | Docker |
| Orchestration | Kubernetes |
| Packaging | Helm |
| Monitoring | Prometheus |
| Dashboards | Grafana |
| Tracing | OpenTelemetry |

---

## Project Structure

```text
services/
├── sensor-simulator/
├── edge-ingestion/
├── edge-sync/
└── cloud-api/

infrastructure/
├── mosquitto/
├── kubernetes/
└── monitoring/

docs/

tests/
```

---

## System Workflow

1. Simulated IoT devices generate telemetry.
2. Telemetry is published through MQTT.
3. The Edge platform validates incoming messages.
4. Valid telemetry is persisted locally.
5. Anomalous measurements are detected.
6. Data is queued for synchronization.
7. When connectivity is restored, pending telemetry is synchronized with the Cloud.
8. The Cloud stores telemetry for long-term persistence and future analysis.

---

## Key Engineering Concepts

- Edge Computing
- Cloud Computing
- Distributed Systems
- Event-Driven Architecture
- Message Brokers
- Fault Tolerance
- Idempotency
- Infrastructure as Code
- Observability
- Containerization

---

## Roadmap

- [x] MQTT Broker
- [x] Sensor Simulator
- [x] Edge Ingestion Service
- [x] PostgreSQL Persistence (Edge)
- [x] Synchronization Queue (Outbox Pattern)
- [x] Edge Synchronization Service
- [x] Cloud Synchronization
- [x] FastAPI
- [x] PostgreSQL Persistence (Cloud)
- [x] Prometheus
- [x] Grafana
- [ ] OpenTelemetry
- [ ] Docker Compose for application services
- [ ] Kubernetes
- [ ] Helm

---

## Project Status

This project is currently under active development.

The first milestone is complete: the Edge platform receives telemetry from a simulated IoT device through MQTT, validates it (required fields, types and metric/unit consistency), flags anomalous readings, and persists valid messages to a local PostgreSQL database.

The second milestone is also complete: the Edge now synchronizes with the Cloud. Every telemetry row carries a `synced` flag; the Edge Synchronization Service polls for unsynced rows, pushes them in batches to a FastAPI Cloud API, and only marks them as synced after a successful response. The Cloud API upserts on `(device_id, edge_record_id)`, so retried or replayed batches never create duplicates. This was verified end-to-end, including simulating a Cloud outage: pending telemetry stayed queued on the Edge and synchronized automatically once connectivity returned, without data loss or duplication.

The third milestone, observability, is also complete. `edge-ingestion`, `edge-sync` and `cloud-api` each expose a Prometheus `/metrics` endpoint with counters for messages received, rejected, flagged as anomalous, persisted, synced and sync failures. Prometheus scrapes all three; Grafana is provisioned with two datasources — Prometheus for those service metrics, and PostgreSQL Edge queried directly for the pending sync queue depth, since that number already lives in the `telemetry` table and does not need to be duplicated as a metric. An overview dashboard ships versioned in the repo (`infrastructure/grafana/provisioning/dashboards/json/`).

Mosquitto, PostgreSQL (Edge), PostgreSQL (Cloud), Prometheus and Grafana currently run through Docker Compose (`infrastructure/`); the four Python services (`sensor-simulator`, `edge-ingestion`, `edge-sync`, `cloud-api`) still run natively, which will change once they are containerized.

The next milestone focuses on tracing: adding OpenTelemetry to follow a single telemetry record across the Edge and Cloud, before moving on to Kubernetes and Helm.

---

## Getting Started

### Prerequisites

- Docker Desktop (with WSL2 backend, on Windows)
- Python 3.13+

### 1. Start the infrastructure (MQTT broker + PostgreSQL)

```bash
cp .env.example .env
docker compose up -d
```

This starts:

- Eclipse Mosquitto on `localhost:1883`
- PostgreSQL (Edge) on `localhost:5432`, with the `telemetry` table created automatically from `infrastructure/postgres/edge/init.sql`
- PostgreSQL (Cloud) on `localhost:5433`, with its own `telemetry` table created from `infrastructure/postgres/cloud/init.sql`
- Prometheus on `localhost:9090`, configured to scrape the three Python services running on the host (`infrastructure/prometheus/prometheus.yml`)
- Grafana on `localhost:3000` (login with `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` from `.env`), pre-provisioned with the Prometheus and PostgreSQL Edge datasources and the "Santa Maria Edge Platform - Overview" dashboard

### 2. Set up each Python service

Each service under `services/` (`sensor-simulator`, `edge-ingestion`, `edge-sync`, `cloud-api`) has its own virtual environment and dependencies:

```bash
cd services/<service-name>
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

All services read their configuration from the `.env` file at the repository root (loaded automatically via `python-dotenv`), so no manual environment exports are needed.

### 3. Run the services

Each in its own terminal, in this order:

```bash
cd services/cloud-api
./.venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

```bash
cd services/edge-ingestion
./.venv/Scripts/python.exe main.py
```

```bash
cd services/edge-sync
./.venv/Scripts/python.exe main.py
```

```bash
cd services/sensor-simulator
./.venv/Scripts/python.exe main.py
```

You should see the simulator publishing readings, `edge-ingestion` logging each received (and, occasionally, anomalous) message, and `edge-sync` reporting batches synced to the Cloud roughly every 10 seconds.

### 4. Verify persisted data

```bash
docker compose exec postgres-edge psql -U santamaria -d santamaria_edge -c "SELECT id, device_id, value, is_anomalous, synced FROM telemetry ORDER BY id DESC LIMIT 10;"
docker compose exec postgres-cloud psql -U santamaria -d santamaria_cloud -c "SELECT edge_record_id, device_id, value, synced_at FROM telemetry ORDER BY id DESC LIMIT 10;"
```

### 5. Try the resilience scenario

Stop `cloud-api` (`Ctrl+C`) while the other services keep running. Telemetry keeps being validated and stored on the Edge, but `edge-sync` will start logging failed sync attempts and the `synced` column will stay `false` for new rows. Restart `cloud-api`, and the next `edge-sync` cycle picks up everything that queued up in the meantime — with no duplicates in the Cloud database.

### 6. Watch it in Grafana

Open `http://localhost:3000`, log in, and open the "Santa Maria Edge Platform - Overview" dashboard. While the services and simulator are running you should see the message/anomaly/sync rates move, and the "Pending Sync Queue" panel spike when you stop `cloud-api` and drain back to zero once you restart it.

You can also query the raw metrics directly, without Grafana:

```bash
curl http://localhost:8001/metrics   # edge-ingestion
curl http://localhost:8002/metrics   # edge-sync
curl http://localhost:8000/metrics   # cloud-api
```

### 7. Stop everything

Stop the Python processes with `Ctrl+C`, then:

```bash
docker compose down
```

Add `-v` to also delete the PostgreSQL data volumes.

---

## Future Architecture Decisions

One of the main goals of this project is not only to build a working platform, but also to justify every architectural decision.

Each major technology adopted throughout the project will be documented together with the reasoning behind its selection.

The first architectural decision is:

### Why MQTT?

The system follows a publish/subscribe architecture where IoT devices are decoupled from processing services.

MQTT was chosen because it provides:

- Lightweight communication
- Asynchronous messaging
- Loose coupling between producers and consumers
- Scalability
- Resilience during intermittent connectivity

Future Architecture Decision Records (ADRs) will include topics such as:

- Why PostgreSQL?
- Why FastAPI?
- Why Docker?
- Why Kubernetes?
- Why Helm?
- Why Prometheus?
- Why Grafana?
- Why OpenTelemetry?
- Why Edge Computing?
- Why an Outbox Pattern?
- Why Idempotent Message Processing?

---

## License

This project is licensed under the MIT License.
