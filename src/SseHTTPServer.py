"""SseHTTPRequestHandler: HTTP GET request handler for server-sent events.

SseHTTPRequestHandler is a pure Python class that serves server-sent events to
web browsers. It is only dependent on standard library modules.

See http://dev.w3.org/html5/eventsource/

Created on 31 mei 2013

@author: Pascal van Eck

"""


__version__ = "0.1"

import http.server
import socketserver
import threading
import sys
import logging
import io
import queue
import importlib


class SseHTTPServer(socketserver.ThreadingTCPServer):

    def __init__(self, server_address, RequestHandlerClass,
                 bind_and_activate=True):
        self.logger = logging.getLogger(__name__)
        self.allow_reuse_address = True
        socketserver.ThreadingTCPServer.__init__(self, server_address,
                                                 RequestHandlerClass,
                                                 bind_and_activate)

    def handle_error(self, request, client_address):
        self.logger.warning("SseHTTPServer(Thread-%s): handle_error() "
                            "called", threading.current_thread().ident)


class SseHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    """HTTP GET request handler that serves a stream of event messages
    according to the SSE W3C recommendation.

    The only dependency that is not in the Python Standard Library is injected
    via a class variable called event_queue_factory.

    As per the structure of the http.server framework in the Python Standard
    Library, this class is not instantiated directly by application scripts.
    Instead, application scripts instantiate socketserver.TCPserver, providing
    this class (not an instance of this class) as an argument to the
    constructor of socketserver.TCPserver. TCPserver (actually, one of its
    ancestors) in turn instantiates this class once for every incoming
    connection.

    """

    server_version = "SseHTTP/" + __version__

    eventsource_path = "/events"

    event_queue_factory = None

    def __init__(self, request, client_address, server):
        self.response_value = ""
        self.logger = logging.getLogger(__name__)
        self._event_queue = None
        http.server.SimpleHTTPRequestHandler.__init__(self, request,
                                                      client_address, server)

    def setup(self):
        self.logger.debug("SseHTTPRequestHandler(Thread-%s): setup() called",
                         threading.current_thread().ident)
        http.server.SimpleHTTPRequestHandler.setup(self)

    def finish(self):
        self.logger.debug("SseHTTPRequestHandler(Thread-%s): finish() called",
                         threading.current_thread().ident)
        if type(self.wfile) == io.BytesIO:
            self.response_value = self.wfile.getvalue()
            self.logger.debug("SseHTTPRequestHandler: response is %s",
                              str(self.response_value))
        http.server.SimpleHTTPRequestHandler.finish(self)

    def log_message(self, format_str, *args):
        self.logger.info("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format_str % args))

    def do_GET(self):
        """Serve a GET request. If and only if the request is for path
        eventsource_path (by default: /events), then serve events according
        to the SSE W3C recommendation. Otherwise, serve files by delegating to
        SimpleHTTPServer from the Python standard library.
        """
        self.logger.debug("SseHTTPRequestHandler(Thread-%s): do_GET, path=%s",
                         threading.current_thread().ident, self.path)
        threading.current_thread().name = (self.path + "_thread_" +
                                           str(threading.current_thread().ident))
        if self.path == SseHTTPRequestHandler.eventsource_path:
            self._start_event_stream()
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

    def _start_event_stream(self):
        """Initialize event queue, send headers, start sending events."""

        # Register with an event queue, which will be used as event source:
        self._event_queue = self._call_factory("subscribe")
        if self._event_queue is None:
            self.logger.debug("SseHTTPRequestHandler(Thread-%s): no queue, "
                              "stopping this thread",
                              threading.current_thread().ident)
            # As per http://dev.w3.org/html5/eventsource/, a response code
            # of 204 tells the browser not to reconnect:
            self.send_response(204)
            return
        self.logger.debug("SseHTTPRequestHandler(Thread-%s): registered queue, "
                     "start sending events", threading.current_thread().ident)

        # Send HTTP headers:
        self.send_response(200)
        self.send_header("Content-type", "text/event-stream")
        self.end_headers()

        # Start event serving loop:
        self._send_events()

    def _send_events(self):
        """Get message from event queue, check whether correct, and if so,
        send it to client. Repeat until message has event terminate."""
        _message_number = 0
        _stop = False
        while not _stop:
            _message_number += 1
            try:
                _message_contents = self._event_queue.get()
                if self._check_message(_message_contents):
                    self._send_message(_message_contents, _message_number)
                    if _message_contents["event"] == "terminate":
                        _stop = True
            except IOError as ex:
                if ex.errno == 10053 or ex.errno == 10054 or ex.errno == 32:
                    self.logger.info("_SseSender(Thread-{0}): "
                                     "client closed connection.".format(
                                           threading.current_thread().ident))
                    _stop = True
                else:
                    self.logger.warning("_SseSender(Thread-{0}): "
                                        "I/O error({1}): "
                              "{2}".format(threading.current_thread().ident,
                                           ex.errno, ex.strerror))
            except:
                self.logger.error("_SseSender(Thread-{0}): Unexpected error: "
                              "{1}".format(threading.current_thread().ident,
                                           sys.exc_info()[0]))
        self.logger.info("_SseSender(Thread-{0}): stopping _send_events "
                         "loop.".format(threading.current_thread().ident))
        self._call_factory("unsubscribe")

    def _call_factory(self, action):
        if sys.version_info[0] == 2:
            factory_module_name = SseHTTPRequestHandler.event_queue_factory[0]
            factory_function_name = SseHTTPRequestHandler.event_queue_factory[1]
            factory_module = importlib.import_module(factory_module_name)
            factory_function = getattr(factory_module, factory_function_name)
            self._event_queue = factory_function(  # pylint: disable=E1102
                                "Thread-%s" % threading.current_thread().ident,
                                action)
        else:
            if not hasattr(SseHTTPRequestHandler.event_queue_factory,
                           "__call__"):
                self.logger.critical("SseHTTPRequestHandler(Thread-%s): "
                                     "event_queue_factory not callable",
                                     threading.current_thread().ident)
                exit()
            return SseHTTPRequestHandler.event_queue_factory(  # pylint: disable=E1102
                                "Thread-%s" % threading.current_thread().ident,
                                action)

    def _check_message(self, _message_contents):
        """Check whether message complies with expected format."""
        if not type(_message_contents) is dict:
            self.logger.error("Message should be a dict.")
            return False
        if not "event" in _message_contents:
            self.logger.error("Message dict has no event key.")
            return False
        if not "data" in _message_contents:
            self.logger.error("Message dict has no data key.")
            return False
        if not type(_message_contents["event"]) == str:
            self.logger.error("Message event is not a string.")
            return False
        if len(_message_contents["event"]) == 0:
            self.logger.error("Message event cannot be empty.")
            return False
        if not type(_message_contents["data"]) == list:
            self.logger.error("Message data is not a list.")
            return False
        if len(_message_contents["data"]) == 0:
            self.logger.error("Message data cannot be empty list.")
            return False
        return True

    def _send_message(self, _message_contents, _message_number):
        """Format message and send it by writing it to self.wfile."""
        if self.wfile.closed:
            raise RuntimeError("Response object closed.")
        self.logger.debug("SseHTTPRequestHandler(Thread-%s): sending message "
                     " %s: %s.", threading.current_thread().ident,
                     _message_number, _message_contents)
        self.wfile.write(("id: %s\r\n" %
                          _message_number).encode('UTF-8', 'replace'))
        self.wfile.write(("event: %s\r\n" %
                          _message_contents["event"]).encode('UTF-8',
                                                             'replace'))
        for _line in _message_contents["data"]:
            self.wfile.write(("data: %s\r\n" %
                              _line).encode('UTF-8', 'replace'))
        self.wfile.write(b"\r\n")
        self.wfile.flush()


def test(handler_class=SseHTTPRequestHandler,
         server_class=socketserver.ThreadingTCPServer):
    """Starts a server on port 8000."""
    test_queue = queue.Queue()
    test_queue.put({"event": "terminate", "data": ["End of event stream."]})
    SseHTTPRequestHandler.event_queue_factory = lambda subscriber, _: test_queue
    http.server.test(handler_class, server_class)


if __name__ == '__main__':
    test()
