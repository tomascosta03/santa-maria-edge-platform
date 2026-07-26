import random, time, json


DEVICE_ID = "sensor-001"
MEASUREMENTS_INTERVAL_SECONDS = 5

def generate_temperature() -> float:
    return random.uniform(18.0, 28.0)



def build_telemetry_message(temperature: float) -> dict:
    return {
        "device_id": DEVICE_ID,
        "metric": "temperature",
        "value": round(temperature, 1),
        "unit": "celsius",
    }

def main() -> None:
    while True:
        temperature_celsius = generate_temperature()

        telemetry_message = build_telemetry_message(temperature_celsius)
        payload = json.dumps(telemetry_message)
        print(payload)

        time.sleep(MEASUREMENTS_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()