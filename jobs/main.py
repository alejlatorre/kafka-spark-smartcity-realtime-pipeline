import random
import time
import uuid
from datetime import datetime, timedelta

import simplejson as json
from confluent_kafka import SerializingProducer
from helpers.utils import get_env, json_serializer

# import logging

# logger = logging.getLogger("test")
# logger.setLevel(logging.DEBUG)

LONDON_COORDINATES = {"latitude": 51.5074, "longitude": -0.1278}
BIRMINGHAM_COORDINATES = {"latitude": 52.4862, "longitude": -1.8904}

# Calculate movement
LATITUDE_INCREMENT = (
    BIRMINGHAM_COORDINATES["latitude"] - LONDON_COORDINATES["latitude"]
) / 100
LONGITUDE_INCREMENT = (
    BIRMINGHAM_COORDINATES["longitude"] - LONDON_COORDINATES["longitude"]
) / 100

# Environment variables for configuration
KAFKA_BOOTSTRAP_SERVERS = get_env("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_SECURITY_PROTOCOL = get_env("KAFKA_SECURITY_PROTOCOL")
VEHICLE_TOPIC = get_env("VEHICLE_TOPIC")
GPS_TOPIC = get_env("GPS_TOPIC")
# TRAFFIC_TOPIC = get_env("TRAFFIC_TOPIC")
# WEATHER_TOPIC = get_env("WEATHER_TOPIC")
# EMERGENCY_TOPIC = get_env("EMERGENCY_TOPIC")

start_time = datetime.now()
start_location = LONDON_COORDINATES.copy()


def simulated_vehicle_movement():
    global start_location

    # Move towards birmingham
    start_location["latitude"] += LATITUDE_INCREMENT
    start_location["longitude"] += LONGITUDE_INCREMENT

    # Add some randomness to simulate actual road travel
    start_location["latitude"] += random.uniform(-0.0005, 0.0005)
    start_location["longitude"] += random.uniform(-0.0005, 0.0005)

    return start_location


def get_next_time():
    global start_time
    start_time += timedelta(seconds=random.randint(30, 60))  # Update frequency
    return start_time


def generate_vehicle_data(device_id):
    location = simulated_vehicle_movement()
    return {
        "id": uuid.uuid4(),
        "deviceId": device_id,
        "timestamp": get_next_time().isoformat(),
        "location": (location["latitude"], location["longitude"]),
        "speed": random.uniform(10, 40),
        "direction": "North-East",
        "make": "BMW",
        "model": "C500",
        "year": 2024,
        "fuelType": "Hybrid",
    }


def generate_gps_data(device_id, timestamp, vehicle_type="private"):
    return {
        "id": uuid.uuid4(),
        "deviceId": device_id,
        "timestamp": timestamp,
        "speed": random.uniform(0, 40),
        "direction": "North-East",
        "vehicleType": vehicle_type,
    }


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce_data_to_kafka(producer, topic, data):
    producer.produce(
        topic,
        key=str(data["id"]),
        value=json.dumps(data, default=json_serializer).encode("utf-8"),
        on_delivery=delivery_report,
    )

    # Delivered synchronously
    producer.flush()


def simulate_journey(producer, device_id):
    while True:
        vehicle_data = generate_vehicle_data(device_id)
        gps_data = generate_gps_data(device_id, vehicle_data["timestamp"])

        produce_data_to_kafka(producer, VEHICLE_TOPIC, vehicle_data)
        produce_data_to_kafka(producer, GPS_TOPIC, gps_data)

        time.sleep(5)


if __name__ == "__main__":
    producer_config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "error_cb": lambda err: print(f"Kafka error: {err}"),
        "security.protocol": KAFKA_SECURITY_PROTOCOL,
    }
    producer = SerializingProducer(producer_config)

    try:
        simulate_journey(producer, "Vehicle-test")
    except KeyboardInterrupt:
        print("Simulation ended by the user")
    except Exception as err:
        print(f"Unexpected error: {err}")
