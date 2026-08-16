import json

import paho.mqtt.client as mqtt


MQTT_CLIENT_ID = "edge-ingestion"
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_KEEPALIVE_SECONDS = 60

MQTT_TOPIC = "santa-maria/telemetry/#"
MQTT_QOS = 0


REQUIRED_TELEMETRY_FIELDS = {
    "device_id",
    "metric",
    "value",
    "unit",
}

SUPPORTED_METRIC_UNITS = {
    "temperature": {"celsius"},
}

ANOMALY_RANGES = {
    "temperature": (-10.0, 50.0),
}

def parse_payload(payload: bytes) -> dict | None:
    try:
        payload_text = payload.decode("utf-8")
        telemetry_message = json.loads(payload_text)

    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"Rejected invalid telemetry payload: {error}")
        return None

    if not isinstance(telemetry_message, dict):
        print("Rejected telemetry payload: expected a JSON object")
        return None

    return telemetry_message


def validate_telemetry_message(telemetry_message: dict) -> bool:
    missing_fields = REQUIRED_TELEMETRY_FIELDS.difference(
        telemetry_message
    )

    if missing_fields:
        formatted_fields = ", ".join(sorted(missing_fields))

        print(
            f"Rejected telemetry message: "
            f"missing required fields: {formatted_fields}"
        )
        return False

    for field_name in ("device_id", "metric", "unit"):
        field_value = telemetry_message[field_name]

        if not isinstance(field_value, str):
            print(
                f"Rejected telemetry message: "
                f"field '{field_name}' must be a string"
            )
            return False

        if not field_value.strip():
            print(
                f"Rejected telemetry message: "
                f"field '{field_name}' cannot be empty"
            )
            return False

    value = telemetry_message["value"]

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        print(
            "Rejected telemetry message: "
            "field 'value' must be a number"
        )
        return False

    metric = telemetry_message["metric"]
    unit = telemetry_message["unit"]

    allowed_units = SUPPORTED_METRIC_UNITS.get(metric)

    if allowed_units is None:
        print(
            f"Rejected telemetry message: "
            f"unsupported metric '{metric}'"
        )
        return False

    if unit not in allowed_units:
        formatted_units = ", ".join(sorted(allowed_units))

        print(
            f"Rejected telemetry message: "
            f"unit '{unit}' is not valid for metric '{metric}'; "
            f"expected one of: {formatted_units}"
        )
        return False

    return True


def is_anomalous_telemetry(telemetry_message: dict) -> bool:
    metric = telemetry_message["metric"]
    value = telemetry_message["value"]

    min_value, max_value = ANOMALY_RANGES[metric]

    return not (min_value <= value <= max_value)


def on_connect(
    client: mqtt.Client,
    _userdata,
    _connect_flags,
    reason_code,
    _properties,
) -> None:
    if reason_code != 0:
        print(f"Failed to connect to MQTT broker: {reason_code}")
        return

    print(
        f"Connected to MQTT broker at "
        f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}"
    )

    result, _message_id = client.subscribe(
        MQTT_TOPIC,
        qos=MQTT_QOS,
    )

    if result == mqtt.MQTT_ERR_SUCCESS:
        print(f"Subscribed to MQTT topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to subscribe to MQTT topic: {result}")


def on_message(
    _client: mqtt.Client,
    _userdata,
    message: mqtt.MQTTMessage,
) -> None:
    telemetry_message = parse_payload(message.payload)

    if telemetry_message is None:
        return

    if not validate_telemetry_message(telemetry_message):
        return

    if is_anomalous_telemetry(telemetry_message):
        print(
            f"Anomalous telemetry detected from {message.topic}: "
            f"{telemetry_message}"
        )

    print(
        f"Received valid telemetry from {message.topic}: "
        f"{telemetry_message}"
    )


def create_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=MQTT_CLIENT_ID,
    )

    client.on_connect = on_connect
    client.on_message = on_message

    return client


def main() -> None:
    mqtt_client = create_mqtt_client()

    try:
        print(
            f"Connecting to MQTT broker at "
            f"{MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}..."
        )

        mqtt_client.connect(
            MQTT_BROKER_HOST,
            MQTT_BROKER_PORT,
            MQTT_KEEPALIVE_SECONDS,
        )

        mqtt_client.loop_forever()

    except KeyboardInterrupt:
        print("\nStopping Edge Ingestion Service...")

    finally:
        mqtt_client.disconnect()


if __name__ == "__main__":
    main()