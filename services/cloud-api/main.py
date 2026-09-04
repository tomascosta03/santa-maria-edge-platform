import os
from contextlib import asynccontextmanager
from datetime import datetime

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from pydantic import BaseModel

load_dotenv()


RECORDS_RECEIVED_TOTAL = Counter(
    "cloud_api_telemetry_records_received_total",
    "Total telemetry records received from Edge nodes",
)


POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5433"))
POSTGRES_DB = os.environ.get("CLOUD_POSTGRES_DB", "santamaria_cloud")
POSTGRES_USER = os.environ.get("CLOUD_POSTGRES_USER", "santamaria")
POSTGRES_PASSWORD = os.environ.get("CLOUD_POSTGRES_PASSWORD", "")


class TelemetryRecord(BaseModel):
    edge_record_id: int
    device_id: str
    metric: str
    value: float
    unit: str
    is_anomalous: bool
    received_at: datetime


def create_postgres_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def persist_telemetry_batch(
    connection: psycopg.Connection,
    records: list[TelemetryRecord],
) -> None:
    with connection.cursor() as cursor:
        for record in records:
            cursor.execute(
                """
                INSERT INTO telemetry (
                    edge_record_id, device_id, metric, value, unit,
                    is_anomalous, received_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (device_id, edge_record_id) DO NOTHING
                """,
                (
                    record.edge_record_id,
                    record.device_id,
                    record.metric,
                    record.value,
                    record.unit,
                    record.is_anomalous,
                    record.received_at,
                ),
            )

    connection.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.postgres_connection = create_postgres_connection()
    yield
    app.state.postgres_connection.close()


app = FastAPI(title="Santa Maria Cloud API", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/telemetry")
def ingest_telemetry(records: list[TelemetryRecord]) -> dict:
    persist_telemetry_batch(app.state.postgres_connection, records)
    RECORDS_RECEIVED_TOTAL.inc(len(records))

    return {"received": len(records)}
