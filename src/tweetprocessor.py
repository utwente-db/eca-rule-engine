'''
Created on 19 jul. 2013

@author: Pascal van Eck
'''

import logging
import SseHTTPServer
import queue
import threading
import actions
import buildinfo
import time

# Module 1.1 in the INF program doesn't teach classes, so we try to avoid
# them. That's why we use three globals, and a classless publish/subscribe
# mechanism.

logger = logging.getLogger(__name__)

BUILDINFO = buildinfo.get_buildinfo(__file__)

LISTENERS = {}

EVENT = threading.Event()

HTTPD = None

STOPPING = False


def process_tweets(port):
    """Main entry point for the server-side component of the Twitter dashboard.
    It has two responsibilities:
    1. Provide an event queue factory to SseHTTPServer.SseHTTPRequestHandler. SseHTTPRequestHandler is the
       piece of Python code that responses to requests sent by the (JavaScript) client running in a browser.
       This piece of code needs to get the contents of its responses from somewhere; to get those responses, it
       calls the factory that we provide here;
    2. Start two components in parallel:
       a. The ECA rule engine that takes tweets from some source, processes them, and based on that puts messages
          in a queue;
       b. A server that listens to a certain port and starts a SseHTTPRequestHandler for every incoming
          connection
    """

    # Responsibility 1: provide factory. This works only on Python 3 because it
    # depends on new-style classes. See older versions in Github for idiom to
    # make it work on Python 2.7.
    SseHTTPServer.SseHTTPRequestHandler.event_queue_factory = publisher

    # Responsibility 2: start server
    global HTTPD
    HTTPD = SseHTTPServer.SseHTTPServer(("", port),
                            SseHTTPServer.SseHTTPRequestHandler)
    HTTPD.serve_forever()


def shutdown_tweetprocessor(reason):
    global STOPPING
    STOPPING = True
    logger.info(reason)
    # 1. Tell all (usually long-running) event stream threads to stop,
    # which releases the socket they're using:
    _send_to_all_listeners({"event": "terminate",
                            "data": [reason]})
    # 2. Wait for all (usually long-running) event stream threads to
    # unsubscribe (which signals that they've stopped):
    while _listener_length() > 0:
        time.sleep(.1)
    # 3. Shutdown server:
    global HTTPD
    if HTTPD is not None:
        HTTPD.shutdown()    


def publisher(listener_id, action):
    """Event source factory for SseHTTPServer.SseHTTPRequestHandler."""
    if action == "subscribe":
        return publisher_subscribe(listener_id)
    else:
        publisher_unsubscribe(listener_id)


def publisher_subscribe(listener_id):
    """Subscribe a new listener.

    Args:
        listener_id: string that identifies the new listeners.

    Returns:
        new queue.Queue instance from which the listener can get messages.
    """

    global STOPPING
    if STOPPING:
        return None
    
    _new_queue = queue.Queue()

    # At least, we want new listeners to know who we are, so the first message
    # we put in the queue is our own identification:
    _new_queue.put(actions.decode(actions.send_buildinfo(BUILDINFO)))

    # We now register the new queue in our LISTENERS dict. Remember that this
    # function is intended to be used as a callback and will be called from a
    # thread. Thanks to Python's Global Interpreter Lock, the following is
    # atomic and will not corrupt the queue, even if multiple threads subscribe
    # at the "same" time
    LISTENERS[listener_id] = _new_queue

    # Threads that fill the queue are assumed to wait until EVENT is set.
    # Currently, the rule engine is honoring that assumption.
    if not EVENT.is_set():
        EVENT.set()

    return _new_queue


def publisher_unsubscribe(listener_id):
    try:
        del LISTENERS[listener_id]
        EVENT.clear()
    except KeyError:
        pass

def _send_to_all_listeners(message):
    for key in LISTENERS:
        LISTENERS[key].put(message)

def _listener_length():
    return len(LISTENERS)

def produce_function(message):
	decoded = actions.decode(message)
	# logger.info('PUBLISH: '+str(decoded))
	# print('PUBLISH: '+str(decoded))
	_send_to_all_listeners(decoded)

def get_produce_function():
	return lambda arg1: produce_function(arg1)

if __name__ == '__main__':
    print("Starting server on port 7737.")
    process_tweets(7737)
