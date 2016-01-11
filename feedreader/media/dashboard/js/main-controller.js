'use strict';
app.controller('mainController',['$scope','$http', function($scope, $http) {
	$scope.username = user_username;
	$scope.avatar = user_avatar;
}]);

app.controller('indexController',['$scope','$http', function($scope, $http) {
	$http.get("/dashboard/api/home/")
	.success(function(data){
		$scope.indexInfo=data.objects;
	});
}]);

app.controller('activityUserController',['$scope','$http', function($scope, $http) {
}]);

app.controller('reportedController',['$http' ,'$scope', function($http, $scope, reported) {
	
	$scope.batchDelete = function() {
		var post_ids = [];
		var singleValues = $( ".checked " );
		singleValues.each(function(index, el) {
			post_ids.push($(this).attr('postId'));

		});
		$http({
			method  : 'POST',
			data    :  'post_ids='+post_ids,
			url     : '/dashboard/api/post/delete/',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		});

	};

	$scope.deletePost = function(cmId) {
		$http({
			method  : 'POST',
			data    :  'post_ids='+ cmId+ ',',
			url     : '/dashboard/api/post/delete/',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}).success(function(data) {
			console.log(data);
		});

		$( "[postId='"+cmId+"']").remove();
	};

	$scope.undoPost = function(cmId) {

		$http({
			method  : 'POST',
			data    : 'post_ids='+ cmId,
			url     : '/dashboard/api/post/report/undo/',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})

	};

	var reported = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "/dashboard/api/post/reported/";
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

	$http.get("/dashboard/api/post/category/chart/")
	.success(function(data){
		var chartInfo= data.objects;
		var pointList= [];
		for (var i=0; i<9; i++) {
			pointList.push({'name':chartInfo.drill_down[0][chartInfo.sub_cat[i].name].name,
				'data':chartInfo.drill_down[0][chartInfo.sub_cat[i].name].data});
		};
		var b = [];
		for (var i=0; i<9; i++) {	
			var a = {
				name: pointList[i].name,
				id: pointList[i].name,
				data: pointList[i].data
			}
			b.push(a);
		};
		console.log(b[1].data);
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
				series: b
			},
			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('adsController',['$scope','$http', function($scope, $http) {
	
	$http.get("/dashboard/api/post/showAds/?date=2015-12-19&ended=0")
	.success(function(data){
		$scope.showPosts= data.objects;
	});

	$http.get("/dashboard/api/ads_stats/?start=2016-01-30&chart_type=line")
	.success(function(data){
		var adsChartInfo= data.objects;
		$scope.highchartsNG ={

			data: {
				cva : adsChartInfo.data
			},

			title: {
				text: 'پست های پروموت شده'
			},

			xAxis: {
                tickInterval: 7 * 24 * 3600 * 1000, // one week
                tickWidth: 0,
                gridLineWidth: 1,
                labels: {
                	align: 'left',
                	x: 3,
                	y: -3
                }
            },

            yAxis: [
            { 
            	title: {
            		text: null
            	},
            	labels: {
            		align: 'left',
            		x: 3,
            		y: 16,
            		format: '{value:.,0f}'
            	},
            	showFirstLabel: false
            },
            { 
            	linkedTo: 0,
            	gridLineWidth: 0,
            	opposite: true,
            	title: {
            		text: null
            	},
            	labels: {
            		align: 'right',
            		x: -3,
            		y: 16,
            		format: '{value:.,0f}'
            	},
            	showFirstLabel: false
            }],

            legend: {
            	align: 'left',
            	verticalAlign: 'top',
            	y: 20,
            	floating: true,
            	borderWidth: 0
            },

            tooltip: {
            	shared: true,
            	crosshairs: true
            },

            plotOptions: {
            	series: {
            		cursor: 'pointer',
            		point: {
            			events: {
            				click: function (e) {
            					hs.htmlExpand(null, {
            						pageOrigin: {
            							x: e.pageX || e.clientX,
            							y: e.pageY || e.clientY
            						},
            						headingText: this.series.name,
            						maincontentText: Highcharts.dateFormat('%A, %b %e, %Y', this.x) + ':<br/> ' +
            						this.y + ' visits',
            						width: 200
            					});
            				}
            			}
            		},
            		marker: {
            			lineWidth: 1
            		}
            	}
            },

            series: [{
            	name: 'پست های پروموت شده',
            	data: adsChartInfo.data,
            	lineWidth: 4,
            	marker: {
            		radius: 4
            	}
            }, {
            	name: 'New visitors'
            }]
        }

    });
}]);

app.controller('blockCtrl',['$scope','$http', function($scope, $http) {
	$http.get("/dashboard/api/block_stats/?start=2015-12-09&end=2015-12-13&chart_type=bar")
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

app.controller('userCtrl',['$scope','$http', function($scope, $http) {
	$http.get("/dashboard/api/user_stats/?start=2015-12-09&end=2015-12-13&chart_type=bar")
	.success(function(data){
		var userChartInfo= data.objects;
		$scope.highchartsNG = {
			options: {
				chart: {
					type: userChartInfo.chart_type
				},
				title: {
					text: 'Browser market shares. January, 2015 to May, 2015'
				},
				subtitle: {
					text: 'تعداد کاربر های به مدت یک ماه'
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
						text: "تعداد کاربر ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> کاربر ها به مدت یک ماه<br/>'
				},
			},
			series: [{
				name: 'کاربر ها',
				colorByPoint: true,
				data: userChartInfo.sub_cat
			}],
			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('followCtrl',['$scope','$http', function($scope, $http) {

	var start_time = $( "#follow_start_value" ).val();
	var end_time = $( "#follow_end_value" ).val();

	$http.get('/dashboard/api/follow_stats/?start='+start_time+'&end='+end_time+'&chart_type=line')
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
	$http.get("/dashboard/api/like_stats/?start=2015-12-09&end=2015-12-28&chart_type=line")
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

app.controller('sellCtrl',['$scope','$http', function($scope, $http) {
	$http.get("/dashboard/api/bill_stats/?start=2015-12-09&end=2016-01-25&chart_type=area")
	.success(function(data){
		var sellChartInfo= data.objects;
		$scope.highchartsNG = {
			options: {
				chart: {
					type: sellChartInfo.chart_type,
					backgroundColor: "transparent",
					colors:['#fff'],
					height: 290
				},
				title: {
					text: 'Browser market shares. January, 2015 to May, 2015',
					style: {
						fontSize:'16px',
						color: '#fff'
					}
					
				},
				subtitle: {
					text: 'فروش ویس به مدت یک ماه',
					style: {
						fontSize:'16px',
						color: '#fff'
					}
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
						text: "فروش ویس"
					}

				},
				yAxis: {
					title:{
						text: "فروش ویس",
						style: {
							fontSize:'16px',
							color: '#fff'
						}
					}

				},


				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> ویس های فروخنه شده به مدت یک ماه<br/>'
				},
			},
			series: [{
				name: 'فروش',
				data: sellChartInfo.data
			}],

			title: {
				text: ''
			},
			loading: false
		}
	});
}]);

app.controller('commentCtrl',['$scope','$http', function($scope, $http) {
	$http.get("/dashboard/api/comment_stats/?start=2015-12-09&end=2015-12-28&chart_type=line")
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

app.controller('logsController',['$scope','$http', function($scope, $http ) {
	$scope.contentValue = 1;
	$scope.actionValue = 1;

	$scope.submitForm = function () {	
		var actionFilter = $scope.contentValue;
		var contentFilter = $scope.actionValue;

		this.logs=[];

		this.url="/dashboard/api/log/show/?content_type="+contentFilter+"&action="+actionFilter;
		$http.get(this.url).success(function(data) {
			$scope.nextUrl = data.meta.next;
			$scope.prevUrl = data.meta.previous;
			var logs = data.objects;
			for (var i = 0; i < logs.length; i++) {
				this.logs.push(logs[i]);
			};
		}.bind(this));
	};
	$scope.next_page= function () {	
		var actionFilter = $scope.contentValue;
		var contentFilter = $scope.actionValue;

		this.logs=[];

		this.url=$scope.nextUrl;
		$http.get(this.url).success(function(data) {
			$scope.nextUrl = data.meta.next;
			$scope.prevUrl = data.meta.previous;
			var logs = data.objects;
			for (var i = 0; i < logs.length; i++) {
				this.logs.push(logs[i]);
			};
		}.bind(this));
	};
	$scope.prev_page= function () {	
		var actionFilter = $scope.contentValue;
		var contentFilter = $scope.actionValue;

		this.logs=[];

		this.url=$scope.prevUrl;
		$http.get(this.url).success(function(data) {
			$scope.nextUrl = data.meta.next;
			$scope.prevUrl = data.meta.previous;
			var logs = data.objects;
			for (var i = 0; i < logs.length; i++) {
				this.logs.push(logs[i]);
			};
		}.bind(this));
	};
}]);

app.controller('searchController',['$scope','$stateParams','$http','$location',function($scope,$stateParams,$http,$location) {

	$scope.showSearchPost = function() {
		console.log("show searh post initialized");
		this.bricks = [];
		this.busy = false;
		this.after = '';
		$stateParams.s_query=this.query;
		this.url = "/dashboard/api/user/search/?q="+$stateParams.s_query;
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

app.controller('viewController',['$scope','$stateParams','$http','$location',function($scope,$stateParams,$http,$location) {

}]);

app.controller('logoutController',function($scope,$http,$location){
	$scope.logout = function() {
		$http.get("/api/v6/auth/logout/")
		.success(function(data) {
			user_token='';
			user_id='';
			$location.path('/login');
		})
	};
});
