import argparse
import json
import threading
import time

import paho.mqtt.client as mqtt


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
        "--messages",
        type=int,
        default=5
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=15
    )

    args = parser.parse_args()

    topic_filter = (
        f"{args.topic_prefix}/#"
    )

    connected = threading.Event()
    complete = threading.Event()

    message_count = 0

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"portfolio-subscriber-{int(time.time())}"
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

        client.subscribe(
            topic_filter
        )


    def on_subscribe(
        client,
        userdata,
        mid,
        reason_code_list,
        properties
    ):

        print(
            f"Subscribed to: {topic_filter}",
            flush=True
        )


    def on_message(
        client,
        userdata,
        msg
    ):

        nonlocal message_count

        message_count += 1

        try:

            data = json.loads(
                msg.payload.decode()
            )

            print(
                "─" * 40,
                flush=True
            )

            print(
                f"Received message #{message_count}",
                flush=True
            )

            print(
                f"Topic: {msg.topic}",
                flush=True
            )

            print(
                f"Location: "
                f"{data.get('location', 'Unknown')}",
                flush=True
            )

            print(
                f"Device ID: "
                f"{data.get('device_id', 'Unknown')}",
                flush=True
            )

            print(
                f"Pressure upstream: "
                f"{data.get('pressure_upstream', 0)} PSI",
                flush=True
            )

            print(
                f"Pressure downstream: "
                f"{data.get('pressure_downstream', 0)} PSI",
                flush=True
            )

            differential = (
                data.get(
                    "pressure_upstream",
                    0
                )
                -
                data.get(
                    "pressure_downstream",
                    0
                )
            )

            print(
                f"Pressure differential: "
                f"{differential:.1f} PSI",
                flush=True
            )

            print(
                f"Flow rate: "
                f"{data.get('flow_rate', 0)} gal/min",
                flush=True
            )

        except json.JSONDecodeError:

            print(
                f"RAW MESSAGE: "
                f"{msg.payload.decode()}",
                flush=True
            )


        if message_count >= args.messages:
            complete.set()


    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message


    print(
        "Starting Hydroficient dashboard subscriber...",
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


    if not complete.wait(
        timeout=args.timeout
    ):

        print(
            "ERROR: Subscriber timed out.",
            flush=True
        )

        client.disconnect()
        client.loop_stop()

        return 1


    print(
        "Subscriber received all demo messages.",
        flush=True
    )

    client.disconnect()
    client.loop_stop()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    