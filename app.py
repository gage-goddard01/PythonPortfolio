from flask import (
    Flask,
    render_template,
    request,
    Response,
    stream_with_context,
)
import random
from apps.password_generator import generate_password
import os
import fcntl
import json
from pathlib import Path
import queue
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# GOOGLE SHEETS API HELPER
REPAIR_SPREADSHEET_ID = os.environ.get("REPAIR_SPREADSHEET_ID")
REPAIR_PRODUCTS_RANGE = "'Website Summary'!A1:W101"
PORTFOLIO_METRICS_RANGE = "'Website Summary'!Y1:Z20"

GOOGLE_SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

_repair_cache = {
    "expires": 0,
    "products": [],
    "metrics": []
}


def get_repair_data():
    now = time.time()

    if (
        _repair_cache["products"]
        and now < _repair_cache["expires"]
    ):
        return (
            _repair_cache["products"],
            _repair_cache["metrics"]
        )

    credentials = Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"],
        scopes=GOOGLE_SHEETS_SCOPES
    )

    service = build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False
    )

    response = (
        service.spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=REPAIR_SPREADSHEET_ID,
            ranges=[
                REPAIR_PRODUCTS_RANGE,
                PORTFOLIO_METRICS_RANGE
            ],
            valueRenderOption="UNFORMATTED_VALUE"
        )
        .execute()
    )

    value_ranges = response.get("valueRanges", [])

    # -------------------------
    # Product data
    # -------------------------

    product_values = []

    if len(value_ranges) >= 1:
        product_values = value_ranges[0].get("values", [])

    products = []

    if len(product_values) >= 2:

        headers = product_values[0]

        for row in product_values[1:]:

            row = row + [""] * (
                len(headers) - len(row)
            )

            product = dict(
                zip(headers, row)
            )

            if not product.get("Product"):
                continue

            products.append(product)

    # -------------------------
    # Portfolio metrics
    # -------------------------

    metric_values = []

    if len(value_ranges) >= 2:
        metric_values = value_ranges[1].get(
            "values",
            []
        )

    metrics = []

    for row in metric_values:

        if len(row) < 2:
            continue

        label = str(row[0]).strip()
        value = row[1]

        if not label:
            continue

        # Ignore the heading row
        if label == "Portfolio Metrics":
            continue

        metrics.append({
            "label": label,
            "value": value
        })

    _repair_cache["products"] = products
    _repair_cache["metrics"] = metrics
    _repair_cache["expires"] = now + 300

    return products, metrics


# MQTT DEMO CONSTANTS
PROJECT_ROOT = Path(__file__).resolve().parent

MQTT_DEMO_DIR = (
    PROJECT_ROOT
    / "demo"
    / "mqtt"
)

MQTT_ORIGINAL_DIR = (
    MQTT_DEMO_DIR
    / "original"
)

MQTT_PUBLISHER_DEMO = (
    MQTT_DEMO_DIR
    / "publisher_demo.py"
)

MQTT_SUBSCRIBER_DEMO = (
    MQTT_DEMO_DIR
    / "subscriber_demo.py"
)

MQTT_ORIGINAL_PUBLISHER = (
    MQTT_ORIGINAL_DIR
    / "module2_sensor.py"
)

MQTT_ORIGINAL_SUBSCRIBER = (
    MQTT_ORIGINAL_DIR
    / "dashboard_subscriber.py"
)

# MQTT DEMO HELPER FUNCTIONS
def mqtt_demo_event(
    event_type,
    **data
):

    payload = {
        "type": event_type,
        **data
    }

    return (
        json.dumps(
            payload,
            separators=(",", ":")
        )
        + "\n"
    )


def mqtt_demo_free_port():

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as sock:

        sock.bind(
            ("127.0.0.1", 0)
        )

        return sock.getsockname()[1]


def mqtt_demo_wait_for_port(
    port,
    process,
    timeout=3
):

    deadline = (
        time.monotonic()
        + timeout
    )

    while (
        time.monotonic()
        < deadline
    ):

        if process.poll() is not None:

            raise RuntimeError(
                "Mosquitto stopped before "
                "the listener became ready."
            )

        try:

            with socket.create_connection(
                ("127.0.0.1", port),
                timeout=0.2
            ):

                return

        except OSError:

            time.sleep(0.05)


    raise RuntimeError(
        "Timed out waiting for Mosquitto."
    )


def mqtt_demo_pump(
    process,
    source,
    output_queue
):

    if process.stdout is None:
        return

    for line in process.stdout:

        line = line.rstrip()

        if line:

            output_queue.put({
                "type": "log",
                "source": source,
                "message": line
            })

    output_queue.put({
        "type": "closed",
        "source": source
    })


def mqtt_demo_stop_process(
    process
):

    if process is None:
        return

    if process.poll() is not None:
        return

    process.terminate()

    try:

        process.wait(
            timeout=2
        )

    except subprocess.TimeoutExpired:

        process.kill()

        process.wait(
            timeout=2
        )


# MAIN FLASK ROUTES
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/health')
def health_check():
    return "OK", 200


@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/password_generator", methods=["GET", "POST"])
def password_generator():
    generated_password = None

    if request.method == "POST":
        password_length = request.form["password_length"]
        password_length = int(password_length)
        generated_password= generate_password(password_length)


    return render_template(
        "password_generator.html",
        generated_password = generated_password
    )

@app.route("/rps", methods=["GET", "POST"])
def rps():

    result = None
    player = None
    computer = None

    if request.method == "POST":

        player = request.form["choice"]

        computer = random.choice(
            ["Rock", "Paper", "Scissors"]
        )

        if player == computer:
            result = "It's a tie!"

        elif (
            (player == "Rock" and computer == "Scissors")
            or (player == "Paper" and computer == "Rock")
            or (player == "Scissors" and computer == "Paper")
        ):
            result = "🎉 You Win!"

        else:
            result = "😢 Computer Wins!"

    return render_template(
        "rps.html",
        result=result,
        player=player,
        computer=computer,
    )

@app.route("/cybersecurity")
def cybersecurity():
    return render_template("cybersecurity.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

### NEW CHANGES
@app.route("/work/elotouch")
def elotouch():

    try:
        repair_products, portfolio_metrics = get_repair_data()

    except Exception:
        app.logger.exception(
            "Unable to retrieve repair portfolio data"
        )

        repair_products = []
        portfolio_metrics = []

    return render_template(
        "elotouch.html",
        repair_products=repair_products,
        portfolio_metrics=portfolio_metrics
    )

@app.route("/work/externship")
def externship():
    return render_template("externship.html")


@app.route("/work/home-lab")
def home_lab():
    return render_template("home_lab.html")

# Top Performer iFrame
@app.route("/credentials/hydroficient")
def hydroficient_credential():
    return render_template("hydroficient_credential.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# MQTT DEMO ROUTE
@app.route(
    "/work/externship/mqtt-demo"
)
def mqtt_demo():

    publisher_source = (
        MQTT_ORIGINAL_PUBLISHER
        .read_text(
            encoding="utf-8"
        )
    )

    subscriber_source = (
        MQTT_ORIGINAL_SUBSCRIBER
        .read_text(
            encoding="utf-8"
        )
    )

    return render_template(
        "mqtt_demo.html",
        publisher_source=publisher_source,
        subscriber_source=subscriber_source
    )

# MQTT DEMO STREAMING EXECUTION ROUTE
@app.route(
    "/api/mqtt-demo/run",
    methods=["POST"]
)
def mqtt_demo_run():

    @stream_with_context
    def generate():

        broker_process = None
        subscriber_process = None
        publisher_process = None

        lock_file = None

        try:

            # ---------------------------------
            # Allow only one live demo at once
            # across Gunicorn workers.
            # ---------------------------------

            lock_file = open(
                "/tmp/gage-mqtt-demo.lock",
                "w"
            )

            try:

                fcntl.flock(
                    lock_file,
                    fcntl.LOCK_EX
                    | fcntl.LOCK_NB
                )

            except BlockingIOError:

                yield mqtt_demo_event(
                    "error",
                    message=(
                        "The MQTT demo is currently "
                        "being used by another visitor. "
                        "Please try again shortly."
                    )
                )

                return


            mosquitto_binary = "/usr/sbin/mosquitto"

            if not os.path.isfile(mosquitto_binary):

                yield mqtt_demo_event(
                    "error",
                    message=(
                        "Mosquitto executable was not found "
                        "on the server."
                        )
                    )

                return

            session_id = (
                uuid.uuid4()
                .hex[:8]
            )

            topic_prefix = (
                f"hydroficient/"
                f"demo/"
                f"{session_id}"
            )

            port = (
                mqtt_demo_free_port()
            )

            output_queue = (
                queue.Queue()
            )


            yield mqtt_demo_event(
                "status",
                message=(
                    "Starting isolated "
                    "MQTT demonstration..."
                )
            )


            with tempfile.TemporaryDirectory(
                prefix="gage-mqtt-demo-"
            ) as temp_directory:

                config_path = (
                    Path(temp_directory)
                    / "mosquitto.conf"
                )

                config_path.write_text(
                    (
                        f"listener {port} "
                        f"127.0.0.1\n"
                        "protocol mqtt\n"
                        "allow_anonymous true\n"
                        "persistence false\n"
                        "connection_messages true\n"
                        "log_dest stdout\n"
                        "log_type all\n"
                        "log_timestamp false\n"
                    ),
                    encoding="utf-8"
                )


                # -----------------------------
                # Start isolated Mosquitto
                # -----------------------------

                broker_process = subprocess.Popen(
                    [
                        mosquitto_binary,
                        "-c",
                        str(config_path)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                threading.Thread(
                    target=mqtt_demo_pump,
                    args=(
                        broker_process,
                        "broker",
                        output_queue
                    ),
                    daemon=True
                ).start()


                mqtt_demo_wait_for_port(
                    port,
                    broker_process
                )


                # -----------------------------
                # Start subscriber first
                # -----------------------------

                subscriber_process = subprocess.Popen(
                    [
                        sys.executable,
                        "-u",
                        str(
                            MQTT_SUBSCRIBER_DEMO
                        ),
                        "--broker",
                        "127.0.0.1",
                        "--port",
                        str(port),
                        "--topic-prefix",
                        topic_prefix,
                        "--messages",
                        "5"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                threading.Thread(
                    target=mqtt_demo_pump,
                    args=(
                        subscriber_process,
                        "subscriber",
                        output_queue
                    ),
                    daemon=True
                ).start()


                # Wait until the subscriber
                # actually confirms subscription.

                subscriber_ready = False

                ready_deadline = (
                    time.monotonic()
                    + 4
                )

                while (
                    time.monotonic()
                    < ready_deadline
                ):

                    try:

                        item = (
                            output_queue.get(
                                timeout=0.25
                            )
                        )

                    except queue.Empty:

                        if (
                            subscriber_process.poll()
                            is not None
                        ):

                            break

                        continue


                    if (
                        item.get("type")
                        == "log"
                    ):

                        yield mqtt_demo_event(
                            "log",
                            source=item["source"],
                            message=item["message"]
                        )


                        if (
                            item["source"]
                            == "subscriber"
                            and
                            item["message"]
                            .startswith(
                                "Subscribed to:"
                            )
                        ):

                            subscriber_ready = True
                            break


                if not subscriber_ready:

                    raise RuntimeError(
                        "Subscriber did not "
                        "become ready."
                    )


                # -----------------------------
                # Start publisher
                # -----------------------------

                publisher_process = subprocess.Popen(
                    [
                        sys.executable,
                        "-u",
                        str(
                            MQTT_PUBLISHER_DEMO
                        ),
                        "--broker",
                        "127.0.0.1",
                        "--port",
                        str(port),
                        "--topic-prefix",
                        topic_prefix,
                        "--count",
                        "5",
                        "--interval",
                        "1"
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                threading.Thread(
                    target=mqtt_demo_pump,
                    args=(
                        publisher_process,
                        "publisher",
                        output_queue
                    ),
                    daemon=True
                ).start()


                # -----------------------------
                # Stream the live demo
                # -----------------------------

                deadline = (
                    time.monotonic()
                    + 20
                )

                while True:

                    try:

                        item = (
                            output_queue.get(
                                timeout=0.25
                            )
                        )

                    except queue.Empty:

                        item = None


                    if (
                        item
                        and
                        item.get("type")
                        == "log"
                    ):

                        yield mqtt_demo_event(
                            "log",
                            source=item["source"],
                            message=item["message"]
                        )


                    publisher_done = (
                        publisher_process.poll()
                        is not None
                    )

                    subscriber_done = (
                        subscriber_process.poll()
                        is not None
                    )


                    if (
                        publisher_done
                        and
                        subscriber_done
                        and
                        output_queue.empty()
                    ):

                        break


                    if (
                        time.monotonic()
                        > deadline
                    ):

                        yield mqtt_demo_event(
                            "error",
                            message=(
                                "The demo exceeded "
                                "its time limit."
                            )
                        )

                        break


                yield mqtt_demo_event(
                    "done",
                    message=(
                        "MQTT demonstration complete."
                    )
                )


        except GeneratorExit:

            raise


        except Exception as error:

            app.logger.exception(
                "MQTT portfolio demo failed"
            )

            yield mqtt_demo_event(
                "error",
                message=(
                    "The MQTT demonstration "
                    "encountered an error."
                )
            )


        finally:

            mqtt_demo_stop_process(
                publisher_process
            )

            mqtt_demo_stop_process(
                subscriber_process
            )

            mqtt_demo_stop_process(
                broker_process
            )


            if lock_file:

                try:

                    fcntl.flock(
                        lock_file,
                        fcntl.LOCK_UN
                    )

                except OSError:

                    pass

                lock_file.close()


    return Response(
        generate(),
        content_type=(
            "application/x-ndjson; "
            "charset=utf-8"
        ),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
