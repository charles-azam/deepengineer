import queue
from typing import Any
from smolagents import Tool


class LoggingTool(Tool):
    """
    Base class for tools that can push logs to a queue.
    """

    def __init__(self, log_queue: queue.Queue | None = None):
        super().__init__()
        self.log_queue = log_queue

    def push_log(self, msg: str):
        if self.log_queue:
            self.log_queue.put(msg)
