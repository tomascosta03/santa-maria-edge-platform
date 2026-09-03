import os
import time

import psycopg
import requests
from dotenv import load_dotenv
from prometheus_client import Counter, start_http_server

load_dotenv()


POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = os.environ.get("EDGE_POSTGRES_DB", "santamaria_edge")
POSTGRES_USER = os.environ.get("EDGE_POSTGRES_USER", "santamaria")
POSTGRES_PASSWORD = os.environ.get("EDGE_POSTGRES_PASSWORD", "")

CLOUD_API_URL = os.environ.get("CLOUD_API_URL", "http://localhost:8000/telemetry")
CLOUD_REQUEST_TIMEOUT_SECONDS = 10

SYNC_INTERVAL_SECONDS = 10
SYNC_BATCH_SIZE = 100

METRICS_PORT = 8002

RECORDS_SYNCED_TOTAL = Counter(
    "edge_sync_records_synced_total",
    "Total telemetry records successfully synced to the Cloud",
)
SYNC_ATTEMPTS_FAILED_TOTAL = Counter(
    "edge_sync_attempts_failed_total",
    "Total sync attempts that failed to reach the Cloud API",
)


def create_postgres_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def fetch_unsynced_telemetry(connection: psycopg.Connection) -> list[dict]:
    with connection.cursor(row_factory=psycopg.rows.dict_row) as cursor:
        cursor.execute(
            """
            SELECT id, device_id, metric, value, unit, is_anomalous, received_at
            FROM telemetry
            WHERE synced = FALSE
            ORDER BY id
            LIMIT %s
            """,
            (SYNC_BATCH_SIZE,),
        )
        return cursor.fetchall()


def build_cloud_payload(telemetry_rows: list[dict]) -> list[dict]:
    return [
        {
            "edge_record_id": row["id"],
            "device_id": row["device_id"],
            "metric": row["metric"],
            "value": row["value"],
            "unit": row["unit"],
            "is_anomalous": row["is_anomalous"],
            "received_at": row["received_at"].isoformat(),
        }
        for row in telemetry_rows
    ]


def send_to_cloud(payload: list[dict]) -> bool:
    try:
        response = requests.post(
            CLOUD_API_URL,
            json=payload,
            timeout=CLOUD_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as error:
        print(f"Failed to reach Cloud API: {error}")
        return False


def mark_as_synced(connection: psycopg.Connection, telemetry_ids: list[int]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE telemetry SET synced = TRUE WHERE id = ANY(%s)",
            (telemetry_ids,),
        )

    connection.commit()


def sync_once(connection: psycopg.Connection) -> int:
    telemetry_rows = fetch_unsynced_telemetry(connection)

    if not telemetry_rows:
        return 0

    payload = build_cloud_payload(telemetry_rows)

    if not send_to_cloud(payload):
        SYNC_ATTEMPTS_FAILED_TOTAL.inc()
        return 0

    telemetry_ids = [row["id"] for row in telemetry_rows]
    mark_as_synced(connection, telemetry_ids)
    RECORDS_SYNCED_TOTAL.inc(len(telemetry_ids))

    print(f"Synced {len(telemetry_ids)} telemetry record(s) to the Cloud")
    return len(telemetry_ids)


def main() -> None:
    start_http_server(METRICS_PORT)
    print(f"Exposing Prometheus metrics on :{METRICS_PORT}/metrics")

    postgres_connection = create_postgres_connection()

    try:
        print(f"Starting Edge Synchronization Service (target: {CLOUD_API_URL})")

        while True:
            sync_once(postgres_connection)
            time.sleep(SYNC_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopping Edge Synchronization Service...")

    finally:
        postgres_connection.close()


if __name__ == "__main__":
    main()
