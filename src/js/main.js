/**
 * main.js: Tweetboard web interface startup code (called directly from 
 * index.html)
 * 
 * @author Pascal van Eck
 * 
 */

define(["jquery", "jasmine-html", "tweetboard"],
    /**
     * Module containing startup code for the Tweetboard web interface. 
     * 
     * This module is explicitly excluded in the Karma setup (needed because
     * it initializes Jasmine). 
     * 
     * @todo Remove dependency on jQuery by creating Jasmine gadget
     * @exports main
     */
    function($, jasmine, tweetboard) {
        "use strict";

        var main = {

            jasmineEnv: jasmine.getEnv(),
            htmlReporter: new jasmine.HtmlReporter(),
            // Module tweetboard exports a singleton, so no new operator here:
            tweetBoard: tweetboard.factory(),

            /**
             * Start the Tweetboard web interface application. Main entry point
             * of the Tweetboard web interface system.
             * 
             * Responsible for starting a Tweetboard object and initializing 
             * the Jasmine test runner.
             * 
             * @method
             * @memberof module:main
             */
            run: function() {

                // Start the Tweetboard application:
                this.tweetBoard.run();

                // Initialize Jasmine JavaScript test runner:
                this.jasmineEnv.updateInterval = 1000;
                this.jasmineEnv.addReporter(this.htmlReporter);
                this.jasmineEnv.specFilter = function(spec) {
                    return this.htmlReporter.specFilter(spec);
                }.bind(this);
                $("#btRunJasmineTests").click(function() {
                    require(["jasmine-html", "jasmine-specs/UTThemeSpec",
                             "jasmine-specs/gadgetSpec",
                             "jasmine-specs/viewSpec"], function() {
                        jasmine.getEnv().execute();
                    });
                });
            }
        };

        return main;
    });
