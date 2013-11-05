#!/usr/bin/env python3
# encoding: utf-8
'''
noDUI.py -- Command-line interface for Twitter dashboard

Based on a template provided by PyDev (Eclipse plugin)

@author:     Pascal van Eck

@copyright:  2013 University of Twente. All rights reserved.

@license:    Creative Commons Attribution

@contact:    p.vaneck@utwente.nl
'''

import sys
import os
import tweetprocessor
import rengine
import logging
import threading
import str2timefloat
from argparse import ArgumentParser, FileType
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013-05-31'
__updated__ = '2013-05-31'

DEBUG = 0
TESTRUN = 0
PROFILE = 0


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def main(argv=None):
    '''Command line options.'''

    global DEBUG

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version,
                                                     program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2013 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    verbose = False
    DEBUG = False
    with_offline_tweets = False

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="set verbosity level [default: %(default)s]")
        parser.add_argument("-d", "--debug", action="store_true",
                            help="produce debug output [default: %(default)s]")
        parser.add_argument("-o", "--with-offline-tweets", action="store_true",
                            help="use offline tweet database [default: %(default)s]")
        parser.add_argument("-r", "--run", action="store_true",
                            help="run without waiting for browser [default: %(default)s]")
        parser.add_argument("-V", "--version", action="version",
                            version=program_version_message)
        parser.add_argument("-p", "--port", type=int, default=7737,
                            metavar="N", help="set port to listen on "
                            "[default: %(default)s]")
        parser.add_argument("-s", "--speed", type=int, default=100000,
                            metavar="N", help="set rule engine speed "
                            "[default: %(default)s]")
        parser.add_argument("-b", "--begin", type=str2timefloat.timefloat, default='',
                            metavar="yyyy-MM-dd[:HH[:mm[:ss]]]", help="set begin date and time [default: first tweet]")
        parser.add_argument("-e", "--end", type=str2timefloat.timefloat, default='',
                            metavar="yyyy-MM-dd[:HH[:mm[:ss]]]", help="set end date [default: last tweet]")
        parser.add_argument("infile", nargs="?", type=FileType("r"),
                            default=sys.stdin, help="file containing event "
                            "messages [default: %(default)s]")

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose
        DEBUG = args.debug  # pylint: disable=W0603
        with_offline_tweets = args.with_offline_tweets
        port = args.port
        speed = args.speed
        begin_time = args.begin
        end_time = args.end
        infile = args.infile

        if verbose > 0:
            logging.basicConfig(level=logging.INFO)

        if DEBUG > 0:
            logging.basicConfig(level=logging.DEBUG)

        # if with_offline_tweets > 0:
            import dboffline as dbconnect
            logging.info("Using offline tweet database")
        # else:
            # import dbconnect
            # logging.info("Using tweets from online database")

        logging.info("noDUI.py: Verbosity level %s.", verbose)
        logging.info("noDUI.py: Running %s, output via port %s.",
                     infile.name, port)

        # Command line parameter processing done, now the real work starts.

        # 1. Connect to the database:
        # TODO: everything's currently hardcoded. Make this more flexible,
        # e.g. by reading settings.ini.
        # try:
            # dbconnect.connect_to_db('130.89.10.35', 'antwan', 'batatweets',
                                    # 'anton_tweets')
        # except Exception as ex:
            # logging.error("Cannot connect to database")
            # return 1
       
        # 2. Try to see if we can parse the input file:
        rengine.load_file_stream(infile)
        
        # 3. Start the server component of the OUI:
        # Tweetprocessor starts a HTTP server that runs forever,
        # so it needs its own thread:
        tweetprocessor_thread = threading.Thread(target = tweetprocessor.process_tweets,
                                                 args = [port],
                                                 name = "tweetprocessor_thread")
        tweetprocessor_thread.start()
        logging.info("Server started.")

        # 4. Start the rule engine:
        # TODO: this needs an observer
        produce_function = tweetprocessor.get_produce_function()
        threadsync_event = tweetprocessor.EVENT
        if args.run:
            threadsync_event = None
        result = rengine.start_rule_engine(start_time = begin_time,
                                  stop_time = end_time,
                                  speed = speed,
                                  produce = produce_function,
                                  threadsync_event = threadsync_event)
        if result:
            logging.error(result)
        else:
            logging.info("Control handed to rule engine")

        # 5. Wait for rule engine to finish (this can be interrupted with CTRL-C):
        while (rengine.engine_thread is not None and
               rengine.engine_thread.is_alive()):
            logging.debug("Rule engine still active")
            rengine.engine_thread.join(0.5)

        # 6. Rule engine has finished. Shut down tweetprocessor:
        cleanup("rule engine stopped")
        return 0

    except KeyboardInterrupt:
        # This exception is raised upon receiving CTRL-C or SIGINT
        cleanup("CTRL-C or SIGINT received")
        return 0
    except Exception as ex:
        if DEBUG or TESTRUN:
            raise(ex)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(ex) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


def cleanup(reason):
    logging.info("Shutdown started, reason: %s.", reason)
    # stop_threads() signals the rule engine and HTTP server thread(s) to stop:
    stop_threads(reason)
    # after being signalled by stop_threads() above, it is very well possible
    # that there are still threads running. It is even possible that a new one
    # has been created because of a quick retry by a connected browser. So we
    # keep on trying. As this code may be called from a KeyboardInterrupt
    # handler, we have to handle our own KeyboardInterrupts.
    while threading.active_count() > 1:
        for _t in threading.enumerate():
            try:
                if _t.name == "rule_engine_thread":
                    rengine.stop_rule_engine()
                    tweetprocessor.EVENT.set()
                if _t != threading.current_thread():
                    logging.debug("Joining thread %s.", _t.name)
                    _t.join(0.1)
            except KeyboardInterrupt:
                stop_threads(reason)
            logging.debug("Active threads: %s, Active listeners: %s.",
                         threading.active_count(),
                         len(tweetprocessor.LISTENERS))
    logging.info("Shutdown completed.")

def stop_threads(reason):
    # rengine.stop_rule_engine() is robust, so we simply call it, won't
    # harm if the rule engine has already stopped or the thread doesn't
    # exist anymore:
    rengine.stop_rule_engine()
    # There are scenarios where the rule engine can't stop because it is
    # still waiting on EVENT to be set, so we set it. It is robust, so no
    # problem if the rule engine has already stopped:
    tweetprocessor.EVENT.set()
    # Stop the HTTP server in a clean way:
    tweetprocessor.shutdown_tweetprocessor(reason)
    

if __name__ == "__main__":
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        PROFILE_FILENAME = 'sseserver_profile.txt'
        cProfile.run('main()', PROFILE_FILENAME)
        STATSFILE = open("profile_stats.txt", "wb")
        P = pstats.Stats(PROFILE_FILENAME, stream=STATSFILE)
        STATS = P.strip_dirs().sort_stats('cumulative')
        STATS.print_stats()
        STATSFILE.close()
        sys.exit(0)
    sys.exit(main())
