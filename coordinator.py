from flask import Flask, request
from sidecar import Sidecar
from flask_cors import CORS
import threading
import time
import math

sidecar = Sidecar("coordinator")
app = Flask(__name__)
CORS(app)


nodes = {
    "proposers": [],
    "acceptors": [],
    "learner": None
}


@app.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to the Coordinator Node!"}


@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    node_type = data.get("type")
    node_url = data.get("url")
    print(f"Registering: {node_type} at {node_url}")
    if not (node_type and node_url):
        return {"error": "Missing type or url"}, 400
    if node_type == "proposer":
        if not any(p["url"] == node_url for p in nodes["proposers"]):
            nodes["proposers"].append({"url": node_url, "range": None})
        else:
            print(f"Proposer {node_url} already registered")
    elif node_type == "acceptor":
        if not any(a["url"] == node_url for a in nodes["acceptors"]):
            nodes["acceptors"].append({"url": node_url})
    elif node_type == "learner":
        nodes["learner"] = {"url": node_url}
    else:
        return {"error": "Invalid node type"}, 400
    assign_ranges()
    broadcast_nodes()
    print(f"Current nodes: {nodes}")
    return {"status": "Registered"}


@app.route("/start", methods=["POST"])
def start():
    data = request.json or {}
    filename = data.get("filename", "sample.txt")
    print(f"Processing file: {filename}")
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
            print(f"Read {len(lines)} lines")
            for line in lines:
                line = line.strip()
                if line:
                    print(f"Sending line to {len(nodes['proposers'])} proposers: {line}")
                    for proposer in nodes["proposers"]:
                        sidecar.send(f"{proposer['url']}/line", {"text": line}, retries=3, delay=1)
        return {"status": "Document processed"}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500


def assign_ranges():
    num_proposers = len(nodes["proposers"])
    print(f"Assigning ranges to {num_proposers} proposers")
    if num_proposers == 0:
        return
    for proposer in nodes["proposers"]:
        proposer["range"] = None
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    letters_per_proposer = max(1, math.ceil(len(letters) / num_proposers))
    for i, proposer in enumerate(nodes["proposers"]):
        start_idx = i * letters_per_proposer
        end_idx = min(start_idx + letters_per_proposer - 1, len(letters) - 1)
        if start_idx < len(letters):
            letter_range = f"{letters[start_idx]}-{letters[end_idx]}"
            proposer["range"] = letter_range
            print(f"Assigned {letter_range} to {proposer['url']}")
            sidecar.send(f"{proposer['url']}/set_range", {"range": letter_range}, retries=3, delay=1)


def broadcast_nodes():
    node_info = {
        "proposers": nodes["proposers"],
        "acceptors": nodes["acceptors"],
        "learner": nodes["learner"]
    }
    print(f"Broadcasting nodes: {node_info}")
    for proposer in nodes["proposers"]:
        sidecar.send(f"{proposer['url']}/nodes", node_info, retries=3, delay=1)
    for acceptor in nodes["acceptors"]:
        sidecar.send(f"{acceptor['url']}/nodes", node_info, retries=3, delay=1)
    if nodes["learner"]:
        sidecar.send(f"{nodes['learner']['url']}/nodes", node_info, retries=3, delay=1)


def run_coordinator():
    print("Coordinator is running on port 5020")

    def send_test_request():
        time.sleep(1)
        sidecar.send("http://127.0.0.1:5020/register",
                     {"type": "proposer", "url": "http://127.0.0.1:5002"},
                     retries=3, delay=1)

    test_thread = threading.Thread(target=send_test_request)
    test_thread.daemon = True
    test_thread.start()

    app.run(host="127.0.0.1", port=5020)