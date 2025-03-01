$(document).ready(function () {


	function graficar(tipo) {

		var div = "main" + tipo.toString()
		var conjunto = "/estadistica/" + tipo.toString()
		var settings = {
			dataType: 'json',
			"crossDomain": true,
			"url": conjunto,
			"method": "GET",
			"headers": {
				"accept": "application/json",
				"Access-Control-Allow-Origin": "*"
			}
		}
		var jqxhr = $.ajax(settings)
			.done(function (dato) {
				var x1 = dato
				var chartOneDom = document.getElementById(div);
				var chartOne = echarts.init(chartOneDom, null, {
					renderer: 'canvas',
					useDirtyRect: false
				});
				var chartOneOption = x1

				if (tipo == 4) {

					var xa = chartOneOption.series[0].data;
					var hours = chartOneOption.xAxis.data;
					var days = chartOneOption.yAxis.data;

					chartOneOption.series[0].data =
						xa.map(function (item) {
							return [item[1], item[0], item[2]];
						});
					chartOneOption.series[0].animationDelay = function (idx) {
						return idx * 5;
					}

					chartOneOption.series[0].symbolSize = function (val) {
						return val[2];
					}
					chartOneOption.tooltip.formatter = function (params) {
						return (
							params.value[2] +
							' tramites, a las ' +
							hours[params.value[0]] +
							' de un ' +
							days[params.value[1]]
						);
					}
				}

				if (tipo == 5) {

					const title = [];
					const singleAxis = [];
					const series = [];
					var xa = chartOneOption.series[0].data;
					var hours = chartOneOption.xAxis.data;
					var days = chartOneOption.yAxis.data;
					days.forEach(function (day, idx) {
						title.push({
							textBaseline: 'middle',
							top: ((idx + 0.5) * 100) / 7 + '%',
							text: day
						});
						singleAxis.push({
							left: 150,
							type: 'category',
							boundaryGap: false,
							data: hours,
							top: (idx * 100) / 7 + 5 + '%',
							height: 100 / 7 - 10 + '%',
							axisLabel: {
								interval: 2
							}
						});
						series.push({
							singleAxisIndex: idx,
							coordinateSystem: 'singleAxis',
							type: 'scatter',
							data: [],
							symbolSize: function (dataItem) {
								return dataItem[1];
							}
						});
					});
					xa.forEach(function (dataItem) {
						series[dataItem[0]].data.push([dataItem[1], dataItem[2]]);
					});

					chartOneOption = {
						tooltip: {
							position: 'top'
						},
						title: title,
						singleAxis: singleAxis,
						series: series
					};

				}


				if (chartOneOption && typeof chartOneOption === "object") {
					chartOne.setOption(chartOneOption, true);
				}

				window.addEventListener('resize', chartOneDom.resize);


			})
			.fail(function (err) {
				console.log(err);
			})
			.always(function (lis) {
				console.log(lis);
			});
	}

	graficar(1)
	graficar(2)

});