from __future__ import annotations
import logging
import time

logger = logging.getLogger("voice_agent")

def configure():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

class Timer:
    def __init__(self, operation: str, **fields):
        self.operation = operation
        self.fields = fields
        self.started = 0.0

    def __enter__(self):
        self.started = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed_ms = round((time.perf_counter() - self.started) * 1000, 2)
        logger.info(
            "operation=%s elapsed_ms=%s success=%s fields=%s",
            self.operation, elapsed_ms, exc is None, self.fields,
        )
