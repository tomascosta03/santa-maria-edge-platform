import json
import os
import random
import time

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

load_dotenv()


DEVICE_ID = "sensor-001"

MQTT_CLIENT_ID = f"{DEVICE_ID}-simulator"
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = 1883
MQTT_KEEPALIVE_SECONDS = 60
MQTT_TOPIC = f"santa-maria/telemetry/temperature/{DEVICE_ID}"
MQTT_QOS = 0

MEASUREMENT_INTERVAL_SECONDS = 5

OTEL_EXPORTER_OTLP_ENDPOINT = os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces"
)

trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "sensor-simulator"}))
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT))
)

tracer = trace.get_tracer(__name__)


def generate_temperature() -> float:
    return random.uniform(18.0, 28.0)


def build_telemetry_message(temperature_celsius: float) -> dict:
    return {
        "device_id": DEVICE_ID,
        "metric": "temperature",
        "value": round(temperature_celsius, 1),
        "unit": "celsius",
    }


def on_connect(
    _client,
    _userdata,
    _connect_flags,
    reason_code,
    _properties,
) -> None:
    if reason_code == 0:
        print(
            f"Connected to MQTT broker at "
            f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}"
        )
    else:
        print(f"Failed to connect to MQTT broker: {reason_code}")


def create_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=MQTT_CLIENT_ID,
    )

    client.on_connect = on_connect

    return client


def main() -> None:
    mqtt_client = create_mqtt_client()

    mqtt_client.connect(
        MQTT_BROKER_HOST,
        MQTT_BROKER_PORT,
        MQTT_KEEPALIVE_SECONDS,
    )

    mqtt_client.loop_start()

    try:
        while True:
            with tracer.start_as_current_span("sensor_simulator.publish_reading") as span:
                temperature_celsius = generate_temperature()

                telemetry_message = build_telemetry_message(
                    temperature_celsius
                )
                payload = json.dumps(telemetry_message)
                span.set_attribute("telemetry.value", telemetry_message["value"])

                publish_info = mqtt_client.publish(
                    MQTT_TOPIC,
                    payload,
                    qos=MQTT_QOS,
                )

                if publish_info.rc != mqtt.MQTT_ERR_SUCCESS:
                    print(
                        f"Failed to publish MQTT message: "
                        f"{publish_info.rc}"
                    )
                else:
                    publish_info.wait_for_publish()
                    print(f"Published to {MQTT_TOPIC}: {payload}")

            time.sleep(MEASUREMENT_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopping sensor simulator...")

    finally:
        mqtt_client.disconnect()
        mqtt_client.loop_stop()


if __name__ == "__main__":
    main()