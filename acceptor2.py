from flask import Flask, request
from sidecar import Sidecar
import threading
import time

sidecar = Sidecar("acceptor2")
app = Flask(__name__)
nodes = {"learner": None}


@app.route("/accept", methods=["POST"])
def accept_result():
    data = request.json or {}
    letter_range = data.get("letter_range")
    count = data.get("count", 0)
    words = data.get("words", [])
    print(f"Received: {data}")
    if not letter_range:
        print("Error: Invalid data")
        return {"error": "Invalid data"}, 400
    start, end = letter_range.split("-")
    valid = all(start.lower() <= word[0].lower() <= end.lower() for word in words) if words else True
    print(f"Validation: valid={valid}, count_matches={len(words) == count}")
    if valid and len(words) == count:
        if nodes["learner"]:
            print(f"Sending to learner: {nodes['learner']['url']}")
            sidecar.send(f"{nodes['learner']['url']}/learn",
                         {"letter_range": letter_range, "count": count, "words": words},
                         retries=3, delay=1)
        else:
            print("No learner registered")
        return {"status": "Accepted"}
    return {"error": "Validation failed"}, 400


@app.route("/nodes", methods=["POST"])
def update_nodes():
    global nodes
    nodes = request.json or {}
    print(f"Updated nodes: {nodes}")
    return {"status": "Nodes updated"}


def run_acceptor():
    print("Acceptor is running on port 5005")

    def send_test_request():
        time.sleep(1)
        sidecar.send("http://127.0.0.1:5020/register",
                     {"type": "acceptor", "url": "http://127.0.0.1:5005"},
                     retries=3, delay=1)

    test_thread = threading.Thread(target=send_test_request)
    test_thread.daemon = True
    test_thread.start()

    app.run(host="127.0.0.1", port=5005)