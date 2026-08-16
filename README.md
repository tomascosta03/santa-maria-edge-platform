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
- [ ] Synchronization Queue (Outbox Pattern)
- [ ] Edge Synchronization Service
- [ ] Cloud Synchronization
- [ ] FastAPI
- [ ] PostgreSQL Persistence (Cloud)
- [ ] Prometheus
- [ ] Grafana
- [ ] OpenTelemetry
- [ ] Docker Compose for application services
- [ ] Kubernetes
- [ ] Helm

---

## Project Status

This project is currently under active development.

The first milestone is complete: the Edge platform receives telemetry from a simulated IoT device through MQTT, validates it (required fields, types and metric/unit consistency), flags anomalous readings, and persists valid messages to a local PostgreSQL database.

Mosquitto and PostgreSQL currently run through Docker Compose (`infrastructure/`); the `sensor-simulator` and `edge-ingestion` services still run natively with Python, which will change once they are containerized.

The next milestone focuses on resilience: introducing an outbox-style synchronization queue on the Edge, followed by an Edge Synchronization Service that pushes pending telemetry to the Cloud once connectivity is available.

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

### 2. Set up each Python service

Each service under `services/` has its own virtual environment and dependencies:

```bash
cd services/edge-ingestion
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Repeat for `services/sensor-simulator`.

The `edge-ingestion` service reads its PostgreSQL credentials from the `.env` file at the repository root (loaded automatically via `python-dotenv`), so no manual environment exports are needed.

### 3. Run the services

In one terminal:

```bash
cd services/edge-ingestion
./.venv/Scripts/python.exe main.py
```

In another terminal:

```bash
cd services/sensor-simulator
./.venv/Scripts/python.exe main.py
```

You should see the simulator publishing readings, and `edge-ingestion` logging each received (and, occasionally, anomalous) message.

### 4. Verify persisted data

```bash
docker compose exec postgres-edge psql -U santamaria -d santamaria_edge -c "SELECT * FROM telemetry ORDER BY id DESC LIMIT 10;"
```

### 5. Stop everything

Stop the two Python processes with `Ctrl+C`, then:

```bash
docker compose down
```

Add `-v` to also delete the PostgreSQL data volume.

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
