'''
Created on 19 aug. 2013

@author: Pascal van Eck
'''

import threading
import time
import random
import logging
import actions
import offline_tweets
import json


class QueueFiller(threading.Thread):

    """Thread class that fills queue with heartbeat messages (one per second)
    """

    my_queue = [{"event": "test", "data": ["Line 1 of first message.",
                                          "Line 2 of first message."]},
                {"event": "test", "data": ["Line 1 of second message.",
                                          "Line 2 of second message."]}
               ]

    def __init__(self, publisher_callback, num_of_listeners_callback, event):
        threading.Thread.__init__(self)
        self.publish = publisher_callback
        self.number_of_listeners = num_of_listeners_callback
        self.event = event
        for message in QueueFiller.my_queue:
            self.publish(message)
        self.logger = logging.getLogger(__name__)

    def run(self):
        while True:
            self.event.wait()
            self.logger.info("QueueuFiller: started in thread %s.", self.ident)
            self.publish(actions.message("queueuFiller: started in "
                                                        "server thread %s." %
                                                        self.ident))
            alert_counter = 0
            while self.number_of_listeners() > 0:
                self.logger.info("QueueFiller: %s listeners, %s threads.",
                      self.number_of_listeners(), threading.active_count())
                self.publish(actions.add_point("memusage",
                                               int(time.time()) * 1000,
                                               random.random()))
                self.publish(actions.add_point("listeners",
                                               int(time.time()) * 1000,
                                               random.random()))
                tweetdata = offline_tweets.cache[int(random.random() * 200)][4]
                try:
                    self.publish(actions.add_tweetlist_tweet("allTweets",
                        json.loads(tweetdata)))
                except ValueError:
                    # json.loads throws a ValueError for some tweets that
                    # apparantly contain invalid json.
                    pass
                if random.random() > .9:
                    alert_counter += 1
                    self.publish(actions.alert("Random alert %s!" %
                                                              alert_counter,
                                                              "myAlerter"))
                time.sleep(1)
            self.logger.info("QueueFiller: stopped in thread %s.", self.ident)


def put_initial_messages(_new_queue):
    memusage_chart_options = {"chart": {"type": "spline",
                                     "animation": "Highcharts.svg"
                                   },
                           "title": {"text": "Max RSS of server"},
                           "xAxis": {"type": "datetime",
                                     "tickPixelInterval": 150
                                    },
                           "yAxis": {"title": {"text": "Max RSS in kB"},
                                     "plotLines": [{
                                                    "value": 0,
                                                    "width": 1,
                                                    "color": "#808080"
                                                    }]
                                     },
                           "series": [{"name": "maxrss",
                                       "data": []}]
                           }

    listeners_chart_options = {"chart": {"type": "spline",
                                         "animation": "Highcharts.svg"
                                         },
                               "title": {"text": "Number of listeners"},
                               "xAxis": {"type": "datetime",
                                         "tickPixelInterval": 150
                                         },
                               "yAxis": {"title": {"text": "Listeners"},
                                         "plotLines": [{
                                                        "value": 0,
                                                        "width": 1,
                                                        "color": "#808080"
                                                        }]
                                         },
                               "series": [{"name": "Listeners",
                                           "data": [{"x": (int(time.time()) - 1)
                                                     * 1000, "y":
                                                     random.random()},
                                                    {"x": int(time.time()) *
                                                     1000, "y":
                                                     random.random()}]}]
                               }

    map_options = {"map": {"options": {"zoom": 4,
                                       "center": [78.840319, 16.585922]
                                       }
                           }
                   }

    example_wordcloud = [{"text": "Amsterdam", "weight": 15},
                         {"text": "Rotterdam", "weight": 15},
                         {"text": "Den Haag", "weight": 8},
                         {"text": "Enschede", "weight": 3},
                         {"text": "Hengelo", "weight": 1.5}]

    for index in range(-19, 0):
        new_point = {"x": (int(time.time()) + index) * 1000,
                     "y": random.random()}
        memusage_chart_options["series"][0]["data"].append(new_point)

#     for index in range(-19, 0):
#         new_point = {"x": (int(time.time()) + index) * 1000,
#                      "y": random.random()}
#         listeners_chart_options["series"][0]["data"].append(new_point)

    _new_queue.put(actions.decode(actions.create_alert_gadget("cell0",
                                      "myAlerter", "Alert!")))
    _new_queue.put(actions.decode(actions.create_alert_gadget("cell9",
                                      "serverinfo", "Server information")))
    _new_queue.put(actions.decode(actions.alert("Server started!",
                                                "serverinfo")))
    _new_queue.put(actions.decode(actions.create_maps_gadget("cell3", "myMap1",
                                                             "Tweet geos",
                                                             map_options)))
    _new_queue.put(actions.decode(actions.add_maps_marker("myMap1", 78.840319,
                                        16.585922, "Jan was here!")))
    _new_queue.put(actions.decode(actions.create_tweetlist_gadget("cell4",
                                        "allTweets", "Random tweets")))
    # _new_queue.put(actions.decode(actions.create_wordcloud_gadget("cell5",
                                        # "myWordCloud", "Dutch cities",
                                        # example_wordcloud)))
    _new_queue.put(actions.decode(actions.create_general_chart("cell1",
                                        "memusage", "Server max RSS",
                                        memusage_chart_options)))
    _new_queue.put(actions.decode(actions.create_general_chart("cell2",
                                        "listeners", "Number of listeners",
                                        listeners_chart_options)))
