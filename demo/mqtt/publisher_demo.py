import argparse
import json
import random
import threading
import time

import paho.mqtt.client as mqtt

from datetime import datetime, timezone


def build_reading(device_id, location, counter):

    return {
        "device_id": device_id,
        "location": location,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "counter": counter,
        "pressure_upstream": round(
            82 + random.uniform(-2, 2),
            1
        ),
        "pressure_downstream": round(
            76 + random.uniform(-2, 2),
            1
        ),
        "flow_rate": round(
            40 + random.uniform(-3, 3),
            1
        ),
    }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--broker",
        default="127.0.0.1"
    )

    parser.add_argument(
        "--port",
        type=int,
        required=True
    )

    parser.add_argument(
        "--topic-prefix",
        required=True
    )

    parser.add_argument(
        "--count",
        type=int,
        default=5
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0
    )

    args = parser.parse_args()

    device_id = "GM-HYDROLOGIC-01"
    location = "main-building"

    topic = (
        f"{args.topic_prefix}/"
        f"sensors/{location}/readings"
    )

    connected = threading.Event()

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"portfolio-publisher-{int(time.time())}"
    )


    def on_connect(
        client,
        userdata,
        flags,
        reason_code,
        properties
    ):

        print(
            f"Connected to Mosquitto "
            f"at {args.broker}:{args.port}",
            flush=True
        )

        connected.set()


    client.on_connect = on_connect

    print(
        "Starting Hydroficient sensor publisher...",
        flush=True
    )

    print(
        f"Device ID: {device_id}",
        flush=True
    )

    print(
        f"Location: {location}",
        flush=True
    )

    print(
        f"Topic: {topic}",
        flush=True
    )

    client.connect(
        args.broker,
        args.port,
        keepalive=20
    )

    client.loop_start()

    if not connected.wait(timeout=3):

        print(
            "ERROR: MQTT connection timed out.",
            flush=True
        )

        client.loop_stop()

        return 1


    for counter in range(
        1,
        args.count + 1
    ):

        reading = build_reading(
            device_id,
            location,
            counter
        )

        payload = json.dumps(reading)

        message_info = client.publish(
            topic,
            payload,
            qos=0
        )

        message_info.wait_for_publish(
            timeout=2
        )

        print(
            f"Published reading #{counter}",
            flush=True
        )

        print(
            f"Pressure: "
            f"{reading['pressure_upstream']}/"
            f"{reading['pressure_downstream']} PSI",
            flush=True
        )

        print(
            f"Flow: "
            f"{reading['flow_rate']} gal/min",
            flush=True
        )

        print(
            f"Payload: {payload}",
            flush=True
        )

        if counter < args.count:
            time.sleep(args.interval)


    print(
        "Publisher finished.",
        flush=True
    )

    client.disconnect()
    client.loop_stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())