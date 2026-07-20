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
