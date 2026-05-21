import time
from contextlib import contextmanager

from app.core.logger import logger


@contextmanager
def log_latency(operation_name: str):
    start_time = time.perf_counter()

    try:
        yield

    finally:
        end_time = time.perf_counter()
        duration_seconds = end_time - start_time

        logger.info(
            "Latency measured | operation=%s | duration_seconds=%.3f",
            operation_name,
            duration_seconds,
        )