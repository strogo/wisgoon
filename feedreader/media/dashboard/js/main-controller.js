'use strict';
app.controller('mainController',['$scope','$http', function($scope, $http) {
	$scope.username = user_username;
	$scope.avatar = user_avatar;
}]);

app.controller('indexController',['$scope','$http', function($scope, $http) {
	$http.get("http://127.0.0.1:8000/dashboard/api/home/?token=12345")
	.success(function(data){
		console.log(data);
		$scope.indexInfo=data.objects;
	});
}]);

app.controller('adsController',['$scope','$http', function($scope, $http) {
}]);

app.controller('logsController',['$scope','$http', function($scope, $http) {
}]);

app.controller('activityUserController',['$scope','$http', function($scope, $http) {
}]);

app.controller('reportedController',['$http' ,'$scope', function($http, $scope, reported) {

	$scope.deletePost = function(cmId) {
		$http({
			method  : 'POST',
			data    : 'post_ids='+ cmId,
			url     : 'http://127.0.0.1:8000/dashboard/api/post/delete/?token=12345',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})
	};
	$scope.undoPost = function(cmId) {
		$http({
			method  : 'POST',
			data    : 'post_ids='+ cmId,
			url     : 'http://127.0.0.1:8000/dashboard/api/post/report/undo/?token=12345',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})

	};


	var reported = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "http://127.0.0.1:8000/dashboard/api/post/reported/?token=12345";
	};

	reported.prototype.nextPage = function() {
		if (this.busy || !this.url) return;
		this.busy = true;

		$http.get(this.url).success(function(data) {
			this.url = data.meta.next;
			var bricks = data.objects;

			for (var i = 0; i < bricks.length; i++) {
				this.bricks.push(bricks[i]);
				
			};

			this.busy = false;
		}.bind(this));

		$scope.selectItem = function(br) {
			var id = '#br-'+br;
			if ($(id).hasClass('checked')) {
				$(id).removeClass('checked');
				$(id + ' > a:first-child > span').removeClass('fa-check-square-o').addClass('fa-square-o');
			}else{
				$(id).addClass('checked');
				$(id + ' > a:first-child > span').removeClass('fa-square-o').addClass('fa-check-square-o');				
			}
		};
	};

	$scope.postItem = new reported();
}]);

app.controller('catstatController',['$http','$scope', function($http, $scope, drilldown) {

	$http.get("http://127.0.0.1:8000/dashboard/api/post/category/chart/?token=12345")
	.success(function(data){
		var chartInfo= data.objects;
		var pointList= [];
		for (var i=0; i<9; i++) {
			pointList.push({'name':chartInfo.drill_down[0][chartInfo.sub_cat[i].name]});
		}
// var name = b.objects['drill_down'][0]["جهان خلقت"].name;

		$scope.highchartsNG = {
			options: {
				chart: {
					type: 'pie'
				},
				title: {
					text: 'Browser market shares. January, 2015 to May, 2015'
				},
				subtitle: {
					text: 'تعداد پست های ورودی در هر دست به مدت یک ماه'
				},
				plotOptions: {
					series: {
						dataLabels: {
							enabled: true,
							format: '{point.name}: {point.y}'
						}
					}
				},

				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست به مدت یک ماه<br/>'
				},
			},
			series: [{
				name: 'دسته بندی اصلی',
				colorByPoint: true,
				data: chartInfo.sub_cat
			}],
			drilldown: {
				series: [{
					name: pointList,
					id: pointList,
					data: pointList.data
				}]
			},
			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('adsstatController',['$scope','$http', function($scope, $http) {
	$http.get("http://127.0.0.1:8000/dashboard/api/ads_stats/?start=2015-12-29&chart_type=bar&token=12345")
	.success(function(data){
		var adsChartInfo= data.objects;
		$scope.highchartsNG = {
			options: {
				chart: {
					type: adsChartInfo.chart_type
				},
				title: {
					text: 'Browser market shares. January, 2015 to May, 2015'
				},
				subtitle: {
					text: 'تعداد پست های پروموت شده به مدت یک ماه'
				},
				plotOptions: {
					series: {
						dataLabels: {
							enabled: true,
							format: '{point.name}: {point.y}'
						}
					}
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد پروموت ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست به مدت یک ماه<br/>'
				},
			},
			series: [{
				name: 'پست های پروموت شده',
				colorByPoint: true,
				data: adsChartInfo.data
			}],
			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('blockCtrl',['$scope','$http', function($scope, $http) {
	$http.get("http://127.0.0.1:8000/dashboard/api/block_stats/?start=2015-12-09&end=2015-12-13&chart_type=bar&token=12345")
	.success(function(data){
		var blockChartInfo= data.objects;
		$scope.highchartsNG = {
			options: {
				chart: {
					type: blockChartInfo.chart_type
				},
				title: {
					text: 'Browser market shares. January, 2015 to May, 2015'
				},
				subtitle: {
					text: 'تعداد بلاک های به مدت یک ماه'
				},
				plotOptions: {
					series: {
						dataLabels: {
							enabled: true,
							format: '{point.name}: {point.y}'
						}
					}
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد بلاک ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست به مدت یک ماه<br/>'
				},
			},
			series: [{
				name: 'بلاک ها',
				colorByPoint: true,
				data: blockChartInfo.sub_cat
			}],
			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('followCtrl',['$scope','$http', function($scope, $http) {
	$http.get("http://127.0.0.1:8000/dashboard/api/follow_stats/?start=2015-12-09&end=2015-12-28&chart_type=line&token=12345")
	.success(function(data){
		var folowChartInfo= data.objects;
		$scope.highchartsNG = {
			options: {
				chart: {
					type: folowChartInfo.chart_type
				},
				title: {
					text: 'Browser market shares. January, 2015 to May, 2015'
				},
				subtitle: {
					text: 'تعداد فالو های به مدت یک ماه'
				},
				plotOptions: {
					series: {
						dataLabels: {
							enabled: true,
							format: '{point.y}'
						}
					}
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد فالوها"
					}

				},


				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست به مدت یک ماه<br/>'
				},
			},
			series: [{
				name: 'فالو ها',
				colorByPoint: true,
				data: folowChartInfo.data
			}],
			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('likesCtrl',['$scope','$http', function($scope, $http) {
	$http.get("http://127.0.0.1:8000/dashboard/api/like_stats/?start=2015-12-09&end=2015-12-28&chart_type=line&token=12345")
	.success(function(data){
		var likesChartInfo= data.objects;
		$scope.highchartsNG = {
			options: {
				chart: {
					type: likesChartInfo.chart_type
				},
				title: {
					text: 'Browser market shares. January, 2015 to May, 2015'
				},
				subtitle: {
					text: 'تعداد لایک های به مدت یک ماه'
				},
				plotOptions: {
					series: {
						dataLabels: {
							enabled: true,
							format: '{point.y}'
						}
					}
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد لایک ها"
					}

				},
				yAxis: {
					title:{
						text: "تعداد لایک ها"
					}

				},


				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست به مدت یک ماه<br/>'
				},
			},
			series: [{
				name: 'لایک ها',
				colorByPoint: true,
				data: likesChartInfo.data
			}],
			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('cmCtrl',['$scope','$http', function($scope, $http) {
	$http.get("http://127.0.0.1:8000/dashboard/api/comment_stats/?start=2015-12-09&end=2015-12-28&chart_type=line&token=12345")
	.success(function(data){
		var cmChartInfo= data.objects;
		$scope.highchartsNG = {
			options: {
				chart: {
					type: cmChartInfo.chart_type
				},
				title: {
					text: 'Browser market shares. January, 2015 to May, 2015'
				},
				subtitle: {
					text: 'تعداد نظر های به مدت یک ماه'
				},
				plotOptions: {
					series: {
						dataLabels: {
							enabled: true,
							format: '{point.y}'
						}
					}
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد نظر ها"
					}

				},
				yAxis: {
					title:{
						text: "تعداد نظرات"
					}

				},


				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست به مدت یک ماه<br/>'
				},
			},
			series: [{
				name: 'نظر ها',
				colorByPoint: true,
				data: cmChartInfo.data
			}],
			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('logsCtrl',['$scope','$http', function($scope, $http ,logsInfo) {
	var logsInfo = function() {
		this.logs = [];
		this.url = "http://127.0.0.1:8000/dashboard/api/log/show/?token=12345";

		$http.get(this.url).success(function(data) {
			var logs = data.objects;
			for (var i = 0; i < logs.length; i++) {
				this.logs.push(logs[i]);
			}
		}.bind(this));
	};
	$scope.logsItem = new logsInfo();
}]);

app.controller('searchController',['$scope','$stateParams','$http','$location',function($scope,$stateParams,$http,$location) {

	$scope.showSearchPost = function() {
		console.log("show searh post initialized");
		this.bricks = [];
		this.busy = false;
		this.after = '';
		$stateParams.s_query=this.query;
		this.url = "http://127.0.0.1:8000/dashboard/api/user/search/?token=12345&q="+$stateParams.s_query;
		$scope.nextPage();
	};

	$scope.nextPage = function() {
		if(this.busy){
			return;
		}
		this.busy = true;
		if (!this.query){
			return;
		}

		$http.get(this.url).success(function(data) {
			$location.search('q='+$stateParams.s_query );
			this.url = data.meta.next;
			if (!data.meta.next){
				return;
			}
			var bricks = data.objects;
			for (var i = 0; i < bricks.length; i++) {
				this.bricks.push(bricks[i]);
			}
			this.busy = false;
		}.bind(this));
	};
}]);
