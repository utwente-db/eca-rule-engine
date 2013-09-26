/**
 * view.js: User interface of the Tweetboard Web Interface
 * 
 * @author Pascal van Eck
 * 
 */

define(["jquery", "hcharts", "highcharts_uttheme", "gadget"],
    /**
     * Module defining a singleton that serves as the Javascript representation
     * of the Tweetboard web interface UI. This singleton is responsible for 
     * initializing and maintaining the view model (as known from the
     * MVVM design pattern)
     * 
     * @exports view
     */
    function($, hc, hct, jasmine) {
        "use strict";

        var view = {

            /**
             * Create the View singleton (factory). 
             *
             * @function
             * @memberof module:view
             */
            factory: function() {
                /* The ViewModel: */
                this.chartViews = [];
                this.mapsViews = [];
                this.tweetListViews = [];
                this.wordCloudViews = [];
                this.monitorView = null;
                this.messageView = null;
                this.alertViews = [];
                this.highchartsOptions = hc.setOptions(hct);
                return this;
            },

            /**
             * Create a monitor gadget. 
             *
             * There can only be one monitor gadget. If a monitor gadget has
             * already been created, this method does nothing.
             * @param {String} destination Id of the HTML element to which the
             * gadget is appended
             * @method
             * @memberof module:view
             */
            createMonitor: function(destination) {
                if (!this.monitorView) {
                    // TODO: Check whether destination is an empty element:
                    $(destination).addMonitorGadget({
                        id: "monitorGadget",
                        title: "Message monitor"
                    }, function(theMonitor) {
                        this.monitorView = theMonitor;
                    }.bind(this));
                }
            },

            /**
             * Create a messager gadget. 
             *
             * There can only be one messager gadget. If a monitor gadget has
             * already been created, this method does nothing.
             * @param {String} destination Id of the HTML element to which the
             * gadget is appended
             * @param {eventTypes} An array of strings of event types that can
             * be sent by this gadget
             * @param {Function} buttonHandler Callback for the Update button.
             * Called with two string arguments: the event type and data.
             * @method
             * @memberof module:view
             */
            createMessager: function(destination, eventTypes, buttonHandler) {
                if (!this.messageView) {
                    // TODO: Check whether destination is an empty element:
                    $(destination).addMessageGadget(
                        {
                            id: "testGadget",
                            title: "Local test gadget",
                            placeholder:
                                "Event data in JSON notation.",
                            eventTypes: eventTypes
                        },
                        function(theMessage) {
                            this.messageView = theMessage;
                        }.bind(this),
                        function() {
                            console.log("Button of Messager clicked.");
                            buttonHandler(
                                this.messageView.eventType.val(),
                                this.messageView.eventData.val());
                        }.bind(this));
                }
            },
            
            /**
             * 
             * Create an alert gadget.
             * 
             * @param {String} cell Id of the HTML element to which the
             * gadget is appended
             * @param {String} id A string that serves as reference for the
             * gadget that is created
             * @param {String} title Title of the gadget, will be displayed in
             * the gadget's title bar
             * @method
             * @memberof module:view
             */
            createAlerter: function(cell, id, title) {
                if (!this.alertViews[id]) {
                    $(cell).addAlertGadget({
                        id: id,
                        title: title
                    },
                    function(theAlerter) {
                        this.alertViews[id] = theAlerter;
                    }.bind(this));
                }
            },

            
            /**
             * Create a chart gadget. 
             *
             * already been created, this method does nothing.
             * @param {String} cell Id of the HTML element to which the
             * gadget is appended
             * @param {String} id A string that serves as reference for the
             * gadget that is created
             * @param {String} title Title of the gadget, will be displayed in
             * the gadget's title bar
             * @param {Object} options Chart options as required by
             * HighCharts.JS
             * @method
             * @memberof module:view
             */
            createChartGadget: function(cell, id, title, options) {
                if ($.trim($(cell).html()) !== "") {
                    console.error("Destination " + cell + " should be empty.");
                    return;
                }
                if (this.chartViews.hasOwnProperty(id)) {
                    console.error("A chart with id " + id + " already exists.");
                    return;
                }
                $(cell).addChartGadget({
                    id: id,
                    title: title,
                    chartConfig: options
                }, function(theChart) {
                    this.chartViews[id] = theChart;
                }.bind(this));
            },
            
            /**
             * Create a tweetlist gadget. 
             *
             * already been created, this method does nothing.
             * @param {String} cell Id of the HTML element to which the
             * gadget is appended
             * @param {String} id A string that serves as reference for the
             * gadget that is created
             * @param {String} title Title of the gadget, will be displayed in
             * the gadget's title bar
             * @method
             * @memberof module:view
             */
            createTweetListGadget: function(cell, id, title) {
                if ($.trim($(cell).html()) !== "") {
                    console.error("Destination " + cell + " should be empty.");
                    return;
                }
                if (this.tweetListViews.hasOwnProperty(id)) {
                    console.error("A tweet list with id " + id +
                                  " already exists.");
                    return;
                }
                $(cell).addTweetListGadget({
                    id: id,
                    title: title
                }, function(theTweetList) {
                    this.tweetListViews[id] = theTweetList;
                }.bind(this));
            },
            
            /**
             * Create a wordcloud gadget. 
             *
             * already been created, this method does nothing.
             * @param {String} cell Id of the HTML element to which the
             * gadget is appended
             * @param {String} id A string that serves as reference for the
             * gadget that is created
             * @param {String} title Title of the gadget, will be displayed in
             * the gadget's title bar
             * @method
             * @memberof module:view
             */
            createWordCloudGadget: function(cell, id, title, cloud) {
                if ($.trim($(cell).html()) !== "") {
                    console.error("Destination " + cell + " should be empty.");
                    return;
                }
                if (this.wordCloudViews.hasOwnProperty(id)) {
                    console.error("A word cloud gadget with id " + id +
                                  " already exists.");
                    return;
                }
                $(cell).addWordCloudGadget({
                    id: id,
                    title: title,
                    cloud: cloud
                }, function(theWordCloud) {
                    this.wordCloudViews[id] = theWordCloud;
                }.bind(this));
            },
            
            /**
             * Update wordcloud in existing wordcloud gadget. 
             *
             * already been created, this method does nothing.
             * @param {String} id Reference of the wordcloud that is to be
             * updated
             * @param {Object} cloud New wordcloud data
             * @method
             * @memberof module:view
             */
            updateWordCloudGadget: function(id, cloud) {
                if (!this.wordCloudViews.hasOwnProperty(id)) {
                    console.error("No word cloud gadget with id " + id +
                                  " exists.");
                    return;
                }
                this.wordCloudViews[id].updateWordCloudGadget(cloud);
            },
            
            /**
             * Create a maps gadget. 
             *
             * @param {String} destination Id of the HTML element to which the
             * gadget is appended
             * @method
             * @memberof module:view
             */
            createMapsGadget: function(destination, id, title, options) {
                // TODO: Check whether destination is an empty element:
                // TODO: Check whether map with same id hasn't been created:
                $(destination).addMapsGadget({
                    id: id,
                    title: title,
                    mapsConfig: options
                }, function(theMap) {
                    this.mapsViews[id] = theMap;
                }.bind(this));
            },
            
            addMapsMarker: function(id, lat, long, text) {
                // TODO: Check if mapsViews[id] is defined:
                this.mapsViews[id].gmap3({
                    marker: {
                        latLng: [lat, long],
                        data: text,
                        events: {
                            mouseover: function(marker, event, context) {
                                var map = this.mapsViews[id].gmap3("get");
                                var infowindow = this.mapsViews[id].gmap3({
                                        get: { name: "infowindow" }});
                                if( infowindow ) {
                                    infowindow.open(map, marker);
                                    infowindow.setContent(context.data);
                                } else {
                                    this.mapsViews[id].gmap3({
                                        infowindow: {
                                            anchor: marker,
                                            options: {content: context.data}
                                        }
                                    });
                                }
                            }.bind(this),
                            mouseout: function() {
                                var infowindow = this.mapsViews[id].gmap3({
                                    get: { name: "infowindow" }});
                                if( infowindow ) {
                                    infowindow.close();
                                }
                            }.bind(this)
                        }
                    }
                });
            },
            
            /** 
             * Update an existing chart widget
             * 
             * @param {String} chartOptions Options of new chart as 
             * JSON-formatted string
             * @method
             * @memberof module:view
             */
            updateWidget: function(chartOptions) {
                console.log("Function updateWidget called: " + chartOptions +
                    ".");
                var newOptions = "";
                try {
                    // TODO: check why JSON parsing is needed here:
                    // TODO: change to window.JSON.parse:
                    newOptions = $.parseJSON(chartOptions);
                } catch (e) {
                    alert("parseJSON() raised exception: " +
                        e.toString() + ".");
                }
                // TODO: enable changing any chart, not just the first one:
                var storedDivId = this.chartViews.firstGraph.renderTo.id;
                this.chartViews.firstGraph.destroy();
                if (!("chart" in newOptions)) {
                    newOptions.chart = {renderTo: storedDivId
                    };
                } else {
                    newOptions.chart.renderTo = storedDivId;
                }
                try {
                    this.chartViews.firstGraph = new hc.Chart(
                                    newOptions);
                } catch (e) {
                    alert("HighCharts.Chart() raised exception: " +
                        e.toString() + ".");
                }
            }

        };
        return view;
    });
