"""
Run
===

"""
# TODO: needs a real doc string.

import json
import atexit

import boto
from six.moves import map

from pywincffi.build.config import get_config
from pywincffi.logger import logger

class Message(object):
    """
    A single message from the queue
    """
    def __init__(self, message):
        self.message = message
        self.body = json.loads(self.message.get_body())


class QueueConsumer(object):
    """
    Context manager which will consume events from Amazon SQS.
    """
    SLEEP =
    def __init__(self):
        self.sqs = None
        self.queue = None
        self.events = []

    def __enter__(self):
        config = get_config()
        self.sqs = boto.connect_sqs()
        self.queue = self.sqs.get_queue(
            config.get("queue", "name"),
            owner_acct_id=config.get("queue", "account_id")
        )

        if self.queue is None:
            raise ValueError("Failed to retrieve queue")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: place event(s) back in queue
        if exc_type is not None:
            pass

    def __iter__(self):
        while True:
            messages = self.queue.get_messages()
            logger.debug("Retrieved %s messages from the queue", len(messages))
            for message in messages:
                yield

def messages():
    """Iterator which produces instances of :class:`Message` for processing"""
    config = get_config()
    sqs = boto.connect_sqs()
    queue = sqs.get_queue(
        config.get("queue", "name"),
        owner_acct_id=config.get("queue", "account_id")
    )

    if queue is None:
        raise ValueError("Failed to retrieve queue")

    return map(Message, queue.get_messages(wait_time_seconds=10))

def main():
    while True:
        try:
            for message in messages():
                pass

        except Exception:
            logger.exception("Failed to retrieve messages")
