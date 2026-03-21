import logging
import time
from collections import deque
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/xiaodouobu.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    encoding="utf-8"
)

request_times = deque()

def log_request(latency: float):
    now = time.time()
    request_times.append(now)
    while request_times and request_times[0] < now - 60:
        request_times.popleft()
    qps = len(request_times) / 60
    logging.info(f"latency={latency:.2f}s | QPS(1min)={qps:.2f}")

def get_qps():
    now = time.time()
    while request_times and request_times[0] < now - 60:
        request_times.popleft()
    return len(request_times) / 60