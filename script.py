import argparse

def start_coordinator():
    print("Starting Coordinator node...")
    from coordinator import run_coordinator
    run_coordinator()

def start_proposer(letter_range, port=5002):
    print(f"Starting Proposer node for range {letter_range}...")
    if port == 5002:
        from proposer import run_proposer
    else:
        from proposer2 import run_proposer
    run_proposer(letter_range)

def start_acceptor(port=5003):
    print("Starting Acceptor node...")
    if port == 5003:
        from acceptor import run_acceptor
    else:
        from acceptor2 import run_acceptor
    run_acceptor()

def start_learner():
    print("Starting Learner node...")
    from learner import run_learner
    run_learner()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a node in a distributed consensus system.")
    parser.add_argument("--role", type=str, required=True, choices=["coordinator", "proposer", "proposer2", "acceptor", "acceptor2", "learner"])
    parser.add_argument("--range", type=str, help="Letter range assigned to proposer (e.g., A-C)")
    parser.add_argument("--port", type=int, default=0, help="Port for proposer or acceptor")
    args = parser.parse_args()

    if args.role == "coordinator":
        start_coordinator()
    elif args.role == "proposer":
        if not args.range:
            print("Error: --range is required for proposer role.")
        else:
            start_proposer(args.range, port=5002)
    elif args.role == "proposer2":
        if not args.range:
            print("Error: --range is required for proposer2 role.")
        else:
            start_proposer(args.range, port=5006)
    elif args.role == "acceptor":
        start_acceptor(port=5003)
    elif args.role == "acceptor2":
        start_acceptor(port=5005)
    elif args.role == "learner":
        start_learner()