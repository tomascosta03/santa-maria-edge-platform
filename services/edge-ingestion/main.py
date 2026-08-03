import json

import paho.mqtt.client as mqtt


MQTT_CLIENT_ID = "edge-ingestion"
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_KEEPALIVE_SECONDS = 60

MQTT_TOPIC = "santa-maria/telemetry/#"
MQTT_QOS = 0


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