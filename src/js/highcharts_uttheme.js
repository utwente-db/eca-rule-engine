/**
 * Skies theme for Highcharts JS
 * @author Torstein Hønsi
 */

define({
    colors: ["#3F9C35", "#CF0072", "#FED100", "#0094B3", "#C60C30", "#00675A",
             "#4F2D7F", "#887B1B"],
	chart: {
		className: "skies",
		borderWidth: 0,
		plotShadow: true,
		plotBackgroundColor: {
			linearGradient: [0, 0, 250, 500],
			stops: [
				[0, "rgba(255, 255, 255, 1)"],
				[1, "rgba(255, 255, 255, 0)"]
			]
		},
		plotBorderWidth: 1
	},
	title: {
		style: {
			color: "#3E576F",
			font: "16px Arial Narrow, Arial, Helvetica, sans-serif"
		}
	},
	subtitle: {
		style: {
			color: "#6D869F",
			font: "12px Arial Narrow, Arial, Helvetica, sans-serif"
		}
	},
	xAxis: {
		gridLineWidth: 0,
		lineColor: "#C0D0E0",
		tickColor: "#C0D0E0",
		labels: {
			style: {
				color: "#666",
				fontWeight: "bold"
			}
		},
		title: {
			style: {
				color: "#666",
				font: "12px Arial Narrow, Arial, Helvetica, sans-serif"
			}
		}
	},
	yAxis: {
		alternateGridColor: "rgba(255, 255, 255, .5)",
		lineColor: "#C0D0E0",
		tickColor: "#C0D0E0",
		tickWidth: 1,
		labels: {
			style: {
				color: "#666",
				fontWeight: "bold"
			}
		},
		title: {
			style: {
				color: "#666",
				font: "12px Arial Narrow, Arial, Helvetica, sans-serif"
			}
		}
	},
	legend: {
		itemStyle: {
			font: "9pt Arial Narrow, Arial, sans-serif",
			color: "#3E576F"
		},
		itemHoverStyle: {
			color: "black"
		},
		itemHiddenStyle: {
			color: "silver"
		}
	},
	labels: {
		style: {
			color: "#3E576F"
		}
	}
});
