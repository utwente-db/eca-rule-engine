/**
 * Gadget.js: jQuery plugins to render gadgets.
 * 
 * @author Pascal van Eck
 * 
 */

define(["jquery", "hcharts", "gmap3", "jqcloud"],
    /**
     * Module containing a number of jQuery plugins.
     * 
     * Remember that jQuery plugins (in contrast to jQueryUI plugins) cannot 
     * maintain state. Instead, we bind the gadget to a calling component
     * using callbacks. In terms of the MVVM pattern, these jQuery plugins are
     * proper views, the calling component plays the role of viewmodel.
     * @exports gadget
     * 
     */
    function($, hc) {

    "use strict";
	
	/** 
	 * Create a general gadget and append it to a given element. Expects an 
	 * options object with "id" and "title" keys.
	 * 
	 * Creates a set of hierarchically nested div elements that can be styled
	 * with CSS to look like a gadget. At the deepest level, the elements of
	 * array contents is appended, element by element. Can be chained.
	 * @function addGadget
	 * @param {Object} options Settings object with "id" and "title" keys
	 * @param {Array} contents Contents of the gadget
	 * @memberof module:gadget
	 */
	$.fn.addGadget = function(options, contents) {
		var theGadget = $("<div>").attr("id", options.id).addClass("gadget");
		var theTitle = $("<div>").addClass("gadget-title").text(options.title);
		var theContents = $("<div>").addClass("gadget-contents");
		contents.forEach(function(contentsItem) {
            theContents.append(contentsItem);
		});
		theGadget.append(theTitle);
		theGadget.append(theContents);
		this.append(theGadget);
		return this;
	};
	
	/* jshint -W110 */
	
    /** 
     * Create a gadget containing a chart from the HighCharts library. 
     * 
     * Adds a chart gadget to the current jQuery selection. The selection is
     * decorated with CSS class "chartgadget-cell", the gadget contents with
     * CSS class "chartgadget-contents". Can be chained.
     * @function addChartGadget
     * @param {Object} options Settings object with "id", "title" and 
     * chartConfig keys. The chartConfig key should have a value as expected
     * by HighChartsJS. The value of chartConfig.chart.renderTo is overwritten
     * if it exists. Does nothing if a chart gadget with the same id already
     * exists.
     * @param {Function} addToModel callback to establish binding
     * @memberof module:gadget
     */
    $.fn.addChartGadget = function(options, addToModel) {
        if( options.id !== undefined &&
            $("#" + options.id + "Div").size() > 0 ) {
            return this;
        }
        if( options.id === undefined ) {
            console.error(".addChartGadget called without id key in options.");
            return this;
        }
        var contents = [];
        contents[0] = $("<div>").addClass("chartgadget-contents").attr("id",
                options.id+"Div");
        this.addClass("chartgadget-cell");
		this.addGadget(options, contents);
		if( options.chartConfig === undefined) {
            console.error(
                ".addChartGadget called without chartConfig key in options.");
            return this;
		}
		if( options.chartConfig.chart === undefined ) {
            options.chartConfig.chart = {renderTo: ""};
		}
        options.chartConfig.chart.renderTo = options.id + "Div";
		addToModel(new hc.Chart(options.chartConfig));
		return this;
	};
	
    /** 
     * Create a gadget containing an UI to send messages as if they are 
     * received from the server (for testing purposes).
     * 
     * Expects an options object with "id" and "title" keys. Can be chained.
     * @function addMessageGadget
     * @param {Object} options Settings object with "id" and "title" keys
     * @param {Function} addToModel callback to establish binding
     * @param {Function} clickCallBack Function called when Update button 
     * is clicked
     * @memberof module:gadget
     */
	$.fn.addMessageGadget = function(options, addToModel, clickCallBack) {
		var contents = [];
		contents[0] = $('<select>');
		options.eventTypes.forEach(function(selectOption) {
            contents[0].append(
                $('<option>').attr('value', selectOption).text(selectOption));
		});
		contents[1] = $('<textarea placeholder="' + options.placeholder +
                        '"></textarea>');
		contents[2] = $('<br>');
		contents[3] = $('<button type="button">Update</button>').click(
            clickCallBack);
		this.addGadget(options, contents);
		addToModel({"eventType": contents[0], "eventData": contents[1]});
		return this;
	};
	
    /** 
     * Create a gadget containing a textarea that displays messages.
     * 
     * Expects an options object with "id" and "title" keys. Can be chained.
     * @function addMonitorGadget
     * @param {Object} options Settings object with "id" and "title" keys
     * @param {Function} addToModel callback to establish binding
     * @memberof module:gadget
     */
	$.fn.addMonitorGadget = function(options, addToModel) {
        var contents = [];
        // TODO: remove id attribute, think it is not used anymore:
        contents[0] = $('<textarea id="txMessages" rows="20" width="100%">' +
                        '</textarea>');
		this.addGadget(options, contents);
		addToModel(contents[0]);
		return this;
	};
	
	/**
	 * Create a gadget that shows alerts.
	 * 
	 * Adds an alert gadget to the current jQuery selection. The selection is
	 * decorated with CSS class "alertgadget-cell", the gadget contents with
	 * CSS class "alertgadget". Initially, the gadget is not visible (in CSS
	 * terms: its ""visibility" is "hidden" and its "height" is "0px".
	 * @function addAlertGadget
     * @param {Object} options Settings object with "id" and "title" keys
     * @param {Function} addToModel callback to establish binding
     * @memberof module:gadget
	 */
	$.fn.addAlertGadget = function(options, addToModel) {
        var contents = [];
        // The class is part of the specification (see the JSDoc comment above:
        contents[0] = $('<div class="alertgadget"></div>');
        // The gadget is currently implemented as an <ol>. This is not
        // mandatory according to the specification above:
        contents[0].append("<ol></ol>");
        this.addClass("alertgadget-cell");
        this.addGadget(options, contents);
        addToModel(this);
        this.css("height", "0px").css("visibility", "hidden");
        return this;
	};
	
	/**
	 * Show an alert
	 * 
	 * Adds an alert to the currently selected alert gadget. If the gadget is
	 * currently not visible, it is made visible. The alert disappears after 
	 * 8 seconds. If it was the last alert to be displayed, the entire gadget is
	 * made invisible.
	 * @function newAlert
	 * @param {String} alertText Text of the alert to display
     * @memberof module:gadget
	 */
	$.fn.newAlert = function(alertText) {
        var newItem = $("<li>" + alertText + "</li>");
        this.find("ol").prepend(newItem);
        var currentHeight = parseInt(this.css("height"), 10);
        this.css("height", (currentHeight + 100) + "px")
            .css("visibility", "visible");
        window.setTimeout(function() {
            newItem.remove();
            var currentHeight = parseInt(this.css("height"), 10);
            this.css("height", (currentHeight - 100) + "px");
            if (currentHeight == 100) {
                this.css("height", "0px").css("visibility", "hidden");
            }
        }.bind(this), 8000);
        return this;
    };

    /**
     * Create a gadget that shows a Google map.
     * 
     * Adds a Google maps gadget to the current jQuery selection. The selection
     * is decorated with CSS class "mapsgadget-cell", the gadget contents with
     * CSS class "mapsgadget". 
     * @function addMapsGadget
     * @param {Object} options Settings object with "id" and "title" keys
     * @param {Function} addToModel callback to establish binding
     * @memberof module:gadget
     */
    $.fn.addMapsGadget = function(options, addToModel) {
        var contents = [];
        // The class is part of the specification (see the JSDoc comment above:
        contents[0] = $('<div class="mapsgadget"></div>');
        this.addClass("mapsgadget-cell");
        this.addGadget(options, contents);
        var theMap = contents[0].gmap3(options.mapsConfig);
        addToModel(theMap);
        return this;
    };

    /**
     * Create a gadget that shows a tweetlist (a list of tweets, like Twitter's
     * timeline.
     * 
     * Adds a tweetlist gadget to the current jQuery selection. The selection
     * is decorated with CSS class "tweetlistgadget-cell", the gadget contents
     * with CSS class "tweetlistgadget-contents". 
     * @function addTweetListGadget
     * @param {Object} options Settings object with "id" and "title" keys
     * @param {Function} addToModel callback to establish binding
     * @memberof module:gadget
     */
    $.fn.addTweetListGadget = function(options, addToModel) {
        var contents = [];
        // The class is part of the specification (see the JSDoc comment above:
        contents[0] = $('<ol class="tweetlistgadget-contents ' +
                        'stream-items js-navigable-stream"></ol>');
        this.addClass("tweetlistgadget-cell");
        this.addGadget(options, contents);
        addToModel(this);
        return this;
    };
    
    $.fn.addTweet = function(tweet) {
        // TODO: Check if selection has correct type
        var newItem = $('<li class="js-stream-item stream-item stream-item ' +
                        'expanding-stream-item"></li>');
        var tweetDiv = $('<div class="tweet original-tweet js-stream-tweet ' +
                         'js-actionable-tweet js-profile-popup-actionable ' +
                         'js-original-tweet"></div>');
        var contentDiv = $('<div class="content"></div>');
        var headerDiv = $('<div class="stream-item-header"></div>');

        // Build a tag image and header:
        var aTag1 = $('<a class="account-group js-account-group ' +
                      'js-action-profile js-user-profile-link js-nav"></a>');
        aTag1.attr("href", "http://twitter.com/" + tweet.user.screen_name);
        var avatar = $("<img>").addClass("avatar js-action-profile-avatar");
        avatar.attr("src", tweet.user.profile_image_url);
        aTag1.append(avatar);
        aTag1.append($('<strong class="fullname js-action-profile-name ' +
                       'show-popup-with-id">' + tweet.user.name + '</strong>'));
        aTag1.append($('<span>&rlm;&nbsp;</span>'));
        aTag1.append($('<span class="username js-action-profile-name">' +
                       '<s>@</s><b>' + tweet.user.screen_name + '</b></span>'));
        headerDiv.append(aTag1);
        
        // Build timestamp:
        var smallTag = $('<small class="time"></small>');
        var aTag2 = $('<a class="tweet-timestamp js-permalink js-nav"></a>');
        aTag2.attr("href", "http://twitter.com/" + tweet.user.screen_name +
                   "/status/" + tweet.id);
        aTag2.attr("title", tweet.created_at);
        aTag2.append($('<span class="_timestamp js-short-timestamp ' +
                       'js-relative-timestamp">' + tweet.created_at +
                       '</span>'));
        smallTag.append(aTag2);
        headerDiv.append(smallTag);
        contentDiv.append(headerDiv);
        
        // Build contents:
        var pTag = $('<p class="js-tweet-text tweet-text">' + tweet.text +
                     '</p>');
        contentDiv.append(pTag);

        // Build outer structure of containing divs:
        tweetDiv.append(contentDiv);
        newItem.append(tweetDiv);
        var theGadget = this.find("ol");
        theGadget.prepend(newItem);
        // TODO: remove last one if more than 20
        // alert();
        if (theGadget.children().size() > 4) {
            theGadget.children().last().remove();
        }
        return this;
    };

    /**
     * Create a gadget that shows a word cloud 
     * 
     * Adds a wordcloud gadget to the current jQuery selection. The selection
     * is decorated with CSS class "wordcloudgadget-cell", the gadget contents
     * with CSS class "wordcloudgadget-contents". 
     * @function addWordCloudGadget
     * @param {Object} options Settings object with "id" and "title" keys
     * @param {Function} addToModel callback to establish binding
     * @memberof module:gadget
     */
    $.fn.addWordCloudGadget = function(options, addToModel) {
        if( options.id !== undefined &&
            $("#" + options.id + "Div").size() > 0 ) {
            return this;
        }
        if( options.id === undefined ) {
            console.error(".addWordCloudGadget called without id key in " +
                "options.");
            return this;
        }
        if( options.cloud === undefined ) {
            options.cloud = [{text: "Empty cloud", weight: 15}];
        }
        var contents = [];
        // The class is part of the specification (see the JSDoc comment above:
        contents[0] = $("<div>").addClass("wordcloudgadget-contents").attr("id",
                            options.id+"Div").width("290px").height("290px");
        this.addGadget(options, contents);
        $("#" + options.id + "Div").jQCloud(options.cloud);
        addToModel(this);
        return this;
    };
    
    $.fn.updateWordCloudGadget = function(cloud) {
        var myId = this.children().first().attr("id");
        $("#" + myId + "Div").empty();
        $("#" + myId + "Div").jQCloud(cloud);
        return this;
    }
    
});