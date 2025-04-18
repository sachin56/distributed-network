import requests
import logging
import time

class Sidecar:
    def __init__(self, node_name):
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(filename=f"{node_name}.log", level=logging.INFO)

    def send(self, url, data, retries=3, delay=1):
        for attempt in range(retries):
            try:
                logging.info(f"Sending to {url}: {data}")
                res = requests.post(url, json=data)
                logging.info(f"Response: {res.status_code}")
                return res
            except requests.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
        logging.error(f"All {retries} attempts failed for {url}")
        return None