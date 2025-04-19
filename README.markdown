# Distributed Consensus System

This project implements a distributed consensus system inspired by the Paxos algorithm. It processes text files to count words based on their starting letters, splitting the workload across multiple nodes. The system consists of a Coordinator, Proposers, Acceptors, a Learner, and a web-based frontend for user interaction.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the System](#running-the-system)
- [Using the Frontend](#using-the-frontend)
- [File Structure](#file-structure)
- [Endpoints](#endpoints)
- [Limitations and Improvements](#limitations-and-improvements)
- [License](#license)

## Overview
The Distributed Consensus System processes text files by dividing words into ranges based on their starting letters (e.g., A-M, N-Z). It uses a Paxos-like architecture where:
- **Proposers** process words within their assigned letter ranges and propose word counts.
- **Acceptors** validate the proposed data.
- **Learner** aggregates and stores the final results.
- **Coordinator** manages node registration, assigns ranges, and broadcasts node information.
- **Frontend** provides a web interface to upload files, select ranges, view results, and monitor node status.

The system is designed for educational purposes to demonstrate distributed consensus concepts, with a focus on modularity and extensibility.

## Architecture
The system is composed of the following components, each running as a Flask-based microservice:

1. **Coordinator** (Port 5020):
   - Registers nodes (proposers, acceptors, learner).
   - Assigns letter ranges to proposers (e.g., A-M, N-Z).
   - Broadcasts node information to ensure connectivity.
   - Optionally initiates file processing by sending lines to proposers.

2. **Proposers** (Ports 5002 and 5006):
   - Process text files or lines, counting words within their assigned ranges.
   - Send processed data to acceptors for validation.
   - Two proposers handle A-M and N-Z by default.

3. **Acceptors** (Ports 5003 and 5005):
   - Validate data from proposers (ensuring words match the range and count is correct).
   - Forward valid data to the learner.

4. **Learner** (Port 5004):
   - Aggregates validated data into a result set.
   - Provides results to the frontend, mapping starting letters to word counts and lists.

5. **Frontend** (Static HTML):
   - A web interface built with Bootstrap 5.3.
   - Allows users to select a letter range, upload text files, fetch results, reset the learner, and check node status.

6. **Sidecar**:
   - A utility class for reliable HTTP communication between nodes, with retry logic.

The system uses a distributed consensus workflow where proposers propose word counts, acceptors validate, and the learner finalizes results, orchestrated by the Coordinator.

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- A web browser (for the frontend)
- Optional: A text editor to modify configuration or code

## Installation
1. **Clone the Repository** (or create the project structure):
   ```bash
   git clone <repository-url>
   cd distributed-consensus-system
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Install the required Python packages:
   ```bash
   pip install flask flask-cors requests
   ```
   - `flask`: For running the microservices.
   - `flask-cors`: For handling CORS in the frontend-backend communication.
   - `requests`: For HTTP communication via the Sidecar utility.

4. **Set Up the Project Structure**:
   Ensure the following files are in the project root:
   - `script.py`: Entry point to start nodes.
   - `coordinator.py`: Coordinator service.
   - `proposer.py`: Proposer 1 service (A-M).
   - `proposer2.py`: Proposer 2 service (N-Z).
   - `acceptor.py`: Acceptor 1 service.
   - `acceptor2.py`: Acceptor 2 service.
   - `learner.py`: Learner service.
   - `sidecar.py`: Sidecar utility for communication.
   - `index.html`: Frontend UI.

## Running the System
1. **Start the Nodes**:
   Open separate terminal windows for each node and activate the virtual environment in each. Run the nodes using `script.py` with appropriate arguments:

   ```bash
   # Coordinator (Port 5020)
   python script.py --role coordinator
   ```

   ```bash
   # Proposer 1 (Port 5002, A-M)
   python script.py --role proposer --range A-M --port 5002
   ```

   ```bash
   # Proposer 2 (Port 5006, N-Z)
   python script.py --role proposer2 --range N-Z --port 5006
   ```

   ```bash
   # Acceptor 1 (Port 5003)
   python script.py --role acceptor --port 5003
   ```

   ```bash
   # Acceptor 2 (Port 5005)
   python script.py --role acceptor2 --port 5005
   ```

   ```bash
   # Learner (Port 5004)
   python script.py --role learner
   ```

   Each node will register with the Coordinator and start listening on its designated port.

2. **Access the Frontend**:
     Then navigate to `http://127.0.0.1:5004/`.

## Using the Frontend
1. **Select a Range**:
   - Choose a letter range (A-M or N-Z) from the dropdown to determine which proposer will process the file.

2. **Upload a File**:
   - Select a `.txt` file and click "Upload File".
   - The file is sent to the proposer corresponding to the selected range (Proposer 1 for A-M, Proposer 2 for N-Z).

3. **Fetch Results**:
   - Click "Fetch Results" to retrieve word counts and lists from the learner, displayed in a table.

4. **Reset Learner**:
   - Click "Reset Learner" to clear the learner’s results, resetting the system for a new file.

5. **Check Node Status**:
   - Click "Check Node Status" to view the registered nodes and their ranges (mocked in the current implementation).

Feedback messages appear for each action, indicating success or errors.

## File Structure
```
distributed-consensus-system/
├── script.py         # Entry point to start nodes
├── coordinator.py    # Coordinator service (port 5020)
├── proposer.py       # Proposer 1 service (port 5002, A-M)
├── proposer2.py      # Proposer 2 service (port 5006, N-Z)
├── acceptor.py       # Acceptor 1 service (port 5003)
├── acceptor2.py      # Acceptor 2 service (port 5005)
├── learner.py        # Learner service (port 5004)
├── sidecar.py        # Utility for HTTP communication
├── index.html        # Frontend UI
├── README.md         # This file
├── venv/             # Virtual environment (after setup)
```

## Endpoints
### Coordinator (Port 5020)
- `GET /`: Returns a welcome message.
- `POST /register`: Registers a node with its type and URL.
- `POST /start`: Reads a file and sends lines to proposers (not used by the frontend).

### Proposers (Ports 5002, 5006)
- `POST /line`: Processes a single line of text.
- `POST /upload`: Processes an uploaded text file.
- `POST /set_range`: Sets the proposer’s letter range.
- `POST /nodes`: Updates the node registry.

### Acceptors (Ports 5003, 5005)
- `POST /accept`: Validates proposed data and forwards to the learner.
- `POST /nodes`: Updates the node registry.

### Learner (Port 5004)
- `POST /learn`: Aggregates validated data.
- `GET /results`: Returns the aggregated results.
- `POST /reset`: Clears the result set.
- `POST /nodes`: Updates the node registry.


