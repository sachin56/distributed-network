from flask import Flask, request
from sidecar import Sidecar
import threading
import time
import re
import requests

sidecar = Sidecar("proposer2")
app = Flask(__name__)
letter_range = ""
nodes = {"acceptors": [], "learner": None}
word_counts = {}


def process_line(line, letter_range):
    """Process a single line of text and update word_counts."""
    global word_counts
    if not letter_range:
        return {"error": "Range not set"}
    start, end = letter_range.split("-")
    words = re.findall(r'\b[a-zA-Z]+\b', line.lower())
    print(f"Words found: {words}")
    count = 0
    matched_words = []
    for word in words:
        if word and start.lower() <= word[0].lower() <= end.lower():
            count += 1
            matched_words.append(word)
    print(f"Matched words for {letter_range}: {matched_words}")
    if letter_range not in word_counts:
        word_counts[letter_range] = {"count": 0, "words": []}
    word_counts[letter_range]["count"] += count
    word_counts[letter_range]["words"].extend(matched_words)
    if nodes["acceptors"]:
        for acceptor in nodes["acceptors"][:2]:
            print(f"Sending to {acceptor['url']}: {word_counts[letter_range]}")
            sidecar.send(f"{acceptor['url']}/accept",
                         {"letter_range": letter_range,
                          "count": word_counts[letter_range]["count"],
                          "words": word_counts[letter_range]["words"]},
                         retries=3, delay=1)
    else:
        print("No acceptors registered")
    return {"status": f"Processed line for range {letter_range}"}


@app.route("/line", methods=["POST"])
def receive_line():
    line = request.json.get("text", "")
    print(f"Received line: {line}")
    return process_line(line, letter_range)


@app.route("/upload", methods=["POST"])
def upload_file():
    global word_counts
    if 'file' not in request.files:
        return {"error": "No file provided"}, 400
    file = request.files['file']
    if file.filename == '':
        return {"error": "No file selected"}, 400
    try:
        # Clear proposer state
        word_counts.clear()
        print("Cleared word_counts for new file")

        # Reset learner state
        if nodes["learner"]:
            try:
                sidecar.send(f"{nodes['learner']['url']}/reset", {}, retries=3, delay=1)
                print(f"Sent reset request to learner: {nodes['learner']['url']}")
            except Exception as e:
                print(f"Warning: Failed to reset learner: {e}")
        else:
            print("Warning: No learner registered, skipping reset")

        # Process file
        text = file.read().decode('utf-8', errors='ignore')
        lines = text.splitlines()
        for line in lines:
            if line.strip():
                result = process_line(line, letter_range)
                if "error" in result:
                    return result, 400
        return {"status": f"File processed for range {letter_range}"}
    except Exception as e:
        return {"error": f"Error processing file: {str(e)}"}, 500


@app.route("/set_range", methods=["POST"])
def set_range():
    global letter_range
    new_range = request.json.get("range", "")
    print(f"Attempting to set range: {new_range}")
    if not (isinstance(new_range, str) and "-" in new_range and len(new_range.split("-")) == 2):
        return {"error": "Invalid range format"}, 400
    letter_range = new_range
    print(f"Set range: {letter_range}")
    return {"status": f"Range set to {letter_range}"}


@app.route("/nodes", methods=["POST"])
def update_nodes():
    global nodes
    nodes = request.json or {}
    print(f"Updated nodes: {nodes}")
    return {"status": "Nodes updated"}


def run_proposer(rng):
    global letter_range
    letter_range = rng
    print(f"Proposer is responsible for letter range: {letter_range}")

    def send_test_request():
        time.sleep(1)
        sidecar.send("http://127.0.0.1:5020/register",
                     {"type": "proposer", "url": "http://127.0.0.1:5006"},
                     retries=3, delay=1)

    test_thread = threading.Thread(target=send_test_request)
    test_thread.daemon = True
    test_thread.start()

    app.run(host="127.0.0.1", port=5006)