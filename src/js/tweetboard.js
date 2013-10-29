/**
 * tweetboard.js: Tweetboard web interface application.
 * 
 * @author Pascal van Eck
 * 
 */

define(["jquery", "handlers", "view"],
    /**
     * Module defining a singleton that represents the Tweetboard web interface
     * application. Directly responsible for communicating with the Tweetboard
     * server, which mainly means: requesting an event stream and handling
     * events received via that stream.
     * 
     * @exports tweetboard
     */
    function($, handlers, view) {
        "use strict";

        var tweetboard = {
                        
            /**
             * Create the TweetBoard singleton (factory). 
             * 
             * Responsible for setting handlers for all types of messages the
             * server may send.
             * 
             * @function
             * @memberof module:tweetboard
             */
            factory: function() {
                // Module view exports a singleton, so no new operator here:
                this.myView = view.factory();
                this.myView.createMonitor("#cell7");
                // TODO: handle case where Eventsource is not implemented:
                this.source = new EventSource("events");
                // TODO: eventTypes should be initialized by module handler
                this.eventTypes = ["buildInfo", "message", "addpoint", "appendpoint", "open",
                                   "error", "createAlertGadget", "alert",
                                   "createMapsGadget", "addMapsMarker",
                                   "createChart", "createTweetlistGadget",
                                   "addTweet", "createWordCloudGadget",
                                   "updateWordCloudGadget"];

                /* Initialize eventsource component: */
                for (var eventType in this.eventTypes) {
                    if (this.eventTypes.hasOwnProperty(eventType)) {
                        console.log("Initializing event type " +
                            this.eventTypes[eventType] + ".");
                        this.initEventSource(this.eventTypes[eventType]);
                    }
                }
                
                return this;
            },
            
            /**
             * Start the Tweetboard application. 
             * 
             * Responsible for creating an initial set of gadgets.
             * @method
             * @memberof module:tweetboard
             */
            run: function() {
                this.myView.createMessager("#cell8", this.eventTypes,
                    this.handleLocalMessage.bind(this));
            },
            
            /**
             * Handle an event create locally (as opposed by the server), e.g.
             * by the messager gadget.
             * 
             * Currently used as callback for the "Update" button of the 
             * messager gadget. Creates a new event that looks exactly like an
             * event received from the server and hands this to handleEvent,
             * which is the function that handles events received from the
             * server. 
             * @param {String} eventType Type of the event to send
             * @param {String} eventData Event Data as JSON-formatted string
             * @method
             * @memberof module:tweetboard
             */
            handleLocalMessage: function(eventType, eventData) {
                var event = $.Event(eventType);
                event.data = eventData;
                this.handleEvent(event);
            },
                                    
            /**
             * Handle an event, either created locally or received from the 
             * server.
             * 
             * Every Eventsource event callback (there's one for each type of
             * message) calls this function, which is responsible for decoding
             * the JSON data received and calling the right handler. 
             * @param {Object} event Event created by Eventsource
             * @method
             * @memberof module:tweetboard
             */
            handleEvent: function(event) {
                var logMessage = "EventSource: message received, type is " +
                    event.type + ", data is " + event.data + ".";
                console.log(logMessage);
                this.myView.monitorView.append(logMessage + "\n");
                var handlerName = event.type + "EventReceived";
                if (typeof handlers[handlerName] !== "undefined") {
                    var parsedData = {};
                    try {
                        if (typeof event.data !== "undefined") {
                            parsedData = window.JSON.parse(event.data);
                        } else {
                            // TODO: handle undefinded event data.
                        }
                    } catch (e) {
                        alert("parseJSON() raised exception: " +
                            e.toString() + ".");
                    }
                    handlers[handlerName].call(this, event, parsedData);
                } else {
                    console.log("No handler for event " + event.type + ".");
                }
            },

            /**
             * Add an event listener (callback) for an Eventsource event. 
             * 
             * For every event type, a listener that calls handleEvent is
             * added to the Eventsource. 
             * @param {String} eventType Type of the event 
             * @method
             * @memberof module:tweetboard
             */
            initEventSource: function(eventType) {
                this.source.addEventListener(eventType,
                    (this.handleEvent).bind(this), false);
            }
        };
        return tweetboard;
    });
