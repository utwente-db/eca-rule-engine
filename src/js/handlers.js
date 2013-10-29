/**
 * handlers.js: handler functions for messages sent by the Tweetboard server.
 * 
 * @author Pascal van Eck
 * 
 */

define(["jquery"],
    /**
     * Module defining a singleton containing a set of handler functions, each 
     * with signature "nameEventReceived(event, data)", where "name" is the 
     * name of the message handled by "nameEventReceived".  
     * 
     * @exports handlers
     * 
     * @todo Remove dependency on jQuery by creating a buildinfo gadget
     * @todo Write code that automatically builds array of event types
     */
    function($) {
        "use strict";

        var handlers = {
            
            buildInfoEventReceived: function(event, data) {
                $("#buildinfo").append("This is tweetboard, branch " +
                    data.branch + ", commit " + data.commit + ".<br>");
            },
            
            createChartEventReceived: function(event, data) {
                console.log("message event: " + data);
                this.myView.createChartGadget("#" + data.cell, data.id,
                    data.title, data.options);
            },
            
            createAlertGadgetEventReceived: function(event, data) {
                console.log("message event: " + data);
                // TODO: Check whether cell and id exist:
                this.myView.createAlerter("#" + data.cell, data.id,
                    data.title);
            },
            
            createMapsGadgetEventReceived: function(event, data) {
                console.log("message event: " + data);
                // TODO: Check whether cell, id and options exist:
                this.myView.createMapsGadget("#" + data.cell, data.id,
                    data.title, data.mapConfig);
            },
            
            addMapsMarkerEventReceived: function(event, data) {
                console.log("message event: " + data);
                // TODO: check whether id exists:
                this.myView.addMapsMarker(data.id, data.lat, data.long,
                    data.text);
            },
            
            createTweetlistGadgetEventReceived: function(event, data) {
                console.log("message event: " + data);
                // TODO: Check whether cell, id and options exist:
                this.myView.createTweetListGadget("#" + data.cell, data.id,
                    data.title);
            },
            
            addTweetEventReceived: function(event, data) {
                console.log("message event: " + data);
                // TODO: Check whether data.id exists:
                this.myView.tweetListViews[data.id].addTweet(data.tweet);
            },
            
            createWordCloudGadgetEventReceived: function(event, data) {
                console.log("message event: " + data);
                // TODO: Check whether cell, id and options exist:
                this.myView.createWordCloudGadget("#" + data.cell, data.id,
                    data.title, data.cloud);
            },
            
            updateWordCloudGadgetEventReceived: function(event, data) {
                console.log("message event: " + data);
                // TODO: Check whether cell, id and options exist:
                this.myView.updateWordCloudGadget(data.id, data.cloud);
            },
                            
            alertEventReceived: function(event, data) {
                console.log("alert received: " + data);
                // TODO: Check whether cell and id exist:
                this.myView.alertViews[data.id].newAlert(data.alertText);
            },

            messageEventReceived: function(event, data) {
                console.log("message event:" + data);
                this.myView.monitorView.append("message event:" + data + "\n");
            },

            addpointEventReceived: function(event, data) {
                this.myView.chartViews[data.chartID].series[0].addPoint([
                    data.X, data.Y], true, true);
            },

            appendpointEventReceived: function(event, data) {
                this.myView.chartViews[data.chartID].series[0].addPoint([
                    data.X, data.Y], true, false);
            },

            errorEventReceived: function(event, data) {
                if (e.readyState == EventSource.CLOSED) {
                    console.log("EventSource connection closed.");
                    this.myView.monitorView.append(
                        "EventSource connection closed.\n");
                } else {
                    console.log("EventSource error");
                    this.myView.monitorView.append("EventSource error.\n");
                }
            },

            openEventReceived: function(event, data) {
                console.log("EventSource connection opened.");
                this.myView.monitorView.append(
                    "EventSource connection opened.\n");
            }
            
        };
        return handlers;
    });
