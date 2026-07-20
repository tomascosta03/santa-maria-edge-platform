# santa-maria-edge-platform

A resilient Edge-to-Cloud IoT telemetry platform designed for environments with intermittent connectivity.

The project simulates a distributed IoT infrastructure capable of collecting telemetry from remote devices, processing data locally at the edge, and synchronizing with the cloud once connectivity is restored.

It is being developed as a practical study of distributed systems, IoT, cloud computing, observability and resilient software architectures.

---

## Motivation

Many IoT deployments operate in locations where cloud connectivity cannot be assumed.

Examples include:

- islands
- industrial facilities
- ships
- offshore platforms
- remote scientific stations

In these environments, sensors must continue operating even when the cloud becomes temporarily unavailable.

Traditional cloud-first architectures often assume continuous connectivity, which may lead to:

- data loss
- unavailable services
- duplicated messages
- inconsistent system state

This project explores an alternative architecture where the Edge node becomes the primary execution environment while the Cloud acts as a synchronization and long-term processing layer.

---

## Objectives

The platform should:

- collect telemetry from multiple simulated IoT devices
- process telemetry locally
- validate incoming data
- detect anomalous measurements
- store telemetry on the Edge
- continue operating without cloud connectivity
- synchronize pending data once connectivity returns
- prevent duplicate processing
- expose operational metrics
- demonstrate production-oriented engineering practices

---

## High-Level Architecture

```text
                 EDGE

   IoT Devices
        │
        ▼
 MQTT Broker (Mosquitto)
        │
        ▼
 Edge Ingestion Service
        │
 ┌──────┴─────────┐
 │                │
 ▼                ▼
Edge Database   Synchronization Queue
                     │
                     ▼
                 Cloud API
                     │
                     ▼
              Cloud Database

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
5. Abnormal values are detected.
6. Data is queued for synchronization.
7. Once connectivity is restored, pending messages are synchronized with the cloud.
8. The cloud stores long-term telemetry.

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

- [ ] MQTT Broker
- [ ] Sensor Simulator
- [ ] Edge Ingestion Service
- [ ] PostgreSQL Persistence
- [ ] Cloud Synchronization
- [ ] FastAPI
- [ ] Prometheus
- [ ] Grafana
- [ ] OpenTelemetry
- [ ] Docker Compose
- [ ] Kubernetes
- [ ] Helm

---

## Status

> 🚧 Currently under active development.

---

## Architecture Decisions

One of the main goals of this project is not only to build a working platform, but also to justify every architectural decision.

Each major technology will be documented and motivated throughout the project.

### Why MQTT?

The system follows a publish/subscribe architecture where IoT devices are decoupled from processing services.

MQTT was chosen because it provides:

- Lightweight communication
- Asynchronous messaging
- Loose coupling between producers and consumers
- Scalability
- Resilience during intermittent connectivity

Future architectural decisions will include:

- Why PostgreSQL?
- Why FastAPI?
- Why Docker?
- Why Kubernetes?
- Why Prometheus?
- Why OpenTelemetry?
- Why Edge Computing?
