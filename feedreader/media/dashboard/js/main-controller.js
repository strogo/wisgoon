'use strict';
app.controller('mainController',['$scope','$http', function($scope, $http) {
	$scope.username = user_username;
	$scope.avatar = user_avatar;
}]);

app.controller('indexController',['$scope','$http', '$location', function($scope, $http, $location) {
	$http.get("/dashboard/api/home/")
	.success(function(data){
		$scope.indexInfo=data.objects;
	}).error(function(data){
		$location.path('/accounts/login/');
	});
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
		$( ".checked").remove();
	};

	$scope.deletePost = function(cmId) {
		$http({
			method  : 'POST',
			data    :  'post_ids='+ cmId+ ',',
			url     : '/dashboard/api/post/delete/',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}).success(function(data) {
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
				console.log(bricks[i].user.username);
				console.log(bricks[i].user.profile.user_active);
				console.log(bricks[i].user.profile.userBanne_profile);

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
					text: ''
				},
				subtitle: {
					text: 'تعداد پست های ورودی در هر دست '
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
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست <br/>'
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
app.controller('activeUserController',function($scope,$http,$location) {
	$scope.activeUser = function() {
		$http({
			method  : 'POST',
			url     : '/dashboard/api/user/changeStatus/',
			data    : $.param($scope.formData), 
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}) .success(function(data) {
			$scope.activeDatas=data;
			if ($scope.activeDatas.status) {
				if ($scope.activeDatas.profile.user_active) {
					$('.activeDatasText').text('کاربر فعال است.');
				}else{
					$('.activeDatasText').text('کاربر غیر فعال است.');
				}
			};
		});
	};	
});

app.controller('searchController',function($scope,$http,$stateParams,$location) {
	$scope.banProfile = function() {
		$http({
			method  : 'POST',
			data    :  $.param($scope.formData),
			url     : '/dashboard/api/user/bannedProfile/',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}).success(function(data){
			$scope.banDatas=data;
			if ($scope.banDatas.status) {
				if ($scope.banDatas.profile.user_active) {
					$('.banDatasText').text('پروفایل کاربر فعال است.');
				}else{
					$('.banDatasText').text('پروفایل کاربر غیر فعال است.');
				}
			};
		});
	};

	$scope.banImei = function() {

		$http({
			method  : 'POST',
			data    :  $.param($scope.formData),
			url     : '/dashboard/api/user/bannedImei/',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}).success(function(data){
			$scope.banImeiDatas=data;
			if ($scope.banImeiDatas.status) {
				if ($scope.banImeiDatas.profile.user_active) {
					$('.banImeiText').text('imei کاربر فعال است.');
				}else{
					$('.banImeiText').text('imei کاربر غیر فعال است.');
				}
			};
		});
	};

	$scope.showSearchUser = function() {
		$scope.statusSearch= " ";
		$scope.imei_text= "این کاربر imei ندارد.";
		this.resultItems = [];
		$stateParams.s_query=this.query;
		this.url = "/dashboard/api/user/search/?q="+$stateParams.s_query;
		$scope.searchUser();
	};

	$scope.searchUser= function() {

		$scope.loading = true;
		this.busy = true;
		if (!this.query){
			return;
		}
		$http.get(this.url).success(function(data) {

			$location.search('q='+$stateParams.s_query );
			var resultItems = data.objects;
			if (resultItems.length==0) {
				$scope.statusSearch= "نتیجه ای برای این جست و جو یافت نشد.";
			}
			for (var i = 0; i < resultItems.length; i++) {
				this.resultItems.push(resultItems[i]);
			};

		}.bind(this)).finally(function () {
			$scope.loading = false;
		});
	};

});

app.controller('adsController',['$scope','$http', function($scope, $http) {

	$scope.refresh_ads=function(){
		var start_time = $( "#ads_start_value" ).val();
		var end_time = $( "#ads_end_value" ).val();
		$http.get("/dashboard/api/ads_stats/?start="+start_time+"&end="+end_time+"&chart_type=line")
		.success(function(data){
			var adsChartInfo= data.objects;
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			$scope.highchartsNG = {
				options: { 
					plotOptions: {
						series: {
							cursor: 'pointer',
							events: {
								click: function (event) {
									$scope.loading = true;
									$http.get("/dashboard/api/post/showAds/?date="+event.point.x+"&ended=0")
									.success(function(data){
										$scope.showPosts= data.objects;
									}).finally(function () {
										$scope.loading = false;
									});
								}
							}
						}
					},
				},

				chart: {
					type: adsChartInfo.chart_type
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد آگهی ها"
					}

				},
				title: {
					text: ''
				},
				subtitle: {
					text: 'تعداد آگهی '
				},

				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست <br/>'
				},
				series: [{
					name: 'ads',
					data: adsChartInfo.data,
					marker: {
						symbol: 'circle',
					},
					color: '#7EB6EC'
				}]
			};
		});
};
$scope.refresh_ads();
}]);

app.controller('sellCtrl',['$scope','$http', function($scope, $http) {

	$scope.refresh_sells=function(){
		var start_time = $( "#sell_start_value" ).val();
		var end_time = $( "#sell_end_value" ).val();
		$scope.loading = true;
		$http.get("/dashboard/api/bill_stats/?start="+start_time+"&end="+end_time+"&chart_type=line")
		.success(function(data){
			var sellChartInfo= data.objects;
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			$scope.highchartsNG = {
				chart: {
					backgroundColor: '#78DCDC',
					type: sellChartInfo.chart_type
				},
				title: {
					text: ''
				},
				subtitle: {
					text: ' فروش های '
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد فروش ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست <br/>'
				},
				series: [{
					name: 'sells',
					data: sellChartInfo.data,
					marker: {
						symbol: 'circle',
					},
					color:"#F88AAF"
				}]
			}
			console.log($scope.highchartsNG);
		}).finally(function () {
			$scope.loading = false;
		});
	};
	$scope.refresh_sells();
}]);

app.controller('logsController',['$scope','$http','$stateParams','$location', function($scope, $http, $stateParams,$location ) {
	$scope.contentValue = 1;
	$scope.actionValue = 1;

	$scope.submitForm = function () {	
		var actionFilter = $scope.contentValue;
		var contentFilter = $scope.actionValue;

		this.logs=[];
		$scope.loading = true;
		this.url="/dashboard/api/log/show/?content_type="+contentFilter+"&action="+actionFilter;
		$http.get(this.url).success(function(data) {
			$scope.nextUrl = data.meta.next;
			$scope.prevUrl = data.meta.previous;
			var logs = data.objects;
			for (var i = 0; i < logs.length; i++) {
				this.logs.push(logs[i]);
			};
		}.bind(this))
		.finally(function () {
			$scope.loading = false;
		});
	};
	$scope.next_page= function () {	
		var actionFilter = $scope.contentValue;
		var contentFilter = $scope.actionValue;

		this.logs=[];
		$scope.loading = true;
		this.url=$scope.nextUrl;
		$http.get(this.url).success(function(data) {
			$scope.nextUrl = data.meta.next;
			$scope.prevUrl = data.meta.previous;
			var logs = data.objects;
			for (var i = 0; i < logs.length; i++) {
				this.logs.push(logs[i]);
			};
		}.bind(this))
		.finally(function () {
			$scope.loading = false;
		});
	};
	$scope.prev_page= function () {	
		var actionFilter = $scope.contentValue;
		var contentFilter = $scope.actionValue;

		this.logs=[];
		$scope.loading = true;
		this.url=$scope.prevUrl;
		$http.get(this.url).success(function(data) {
			$scope.nextUrl = data.meta.next;
			$scope.prevUrl = data.meta.previous;
			var logs = data.objects;
			for (var i = 0; i < logs.length; i++) {
				this.logs.push(logs[i]);
			};
		}.bind(this)).finally(function () {
			$scope.loading = false;
		});
	};
	$scope.showSearchLog = function() {
		$scope.statusSearch= " ";
		this.logs = [];
		this.after = '';
		$stateParams.s_query=this.query;
		this.url = "/dashboard/api/log/search/?q="+$stateParams.s_query;
		$scope.searchLog();
	};

	$scope.searchLog = function() {
		$scope.loading = true;
		this.busy = true;
		if (!this.query){
			return;
		}
		$http.get(this.url).success(function(data) {
			$location.search('q='+$stateParams.s_query );
			$scope.nextUrl = data.meta.next;
			$scope.prevUrl = data.meta.previous;
			var logs = data.objects;
			if (logs.length==0) {
				$scope.statusSearch= "نتیجه ای برای این جست و جو یافت نشد.";
			}
			for (var i = 0; i < logs.length; i++) {
				this.logs.push(logs[i]);
			};
		}.bind(this)).finally(function () {
			$scope.loading = false;
		});
	};
}]);

/****** user activity *******/

app.controller('activityUserController',['$scope','$http', function($scope, $http) {
}]);

app.controller('blockCtrl',['$scope','$http', function($scope, $http) {
	$scope.refresh_blocks=function(){
		var start_time = $( "#block_start_value" ).val();
		var end_time = $( "#block_end_value" ).val();
		$scope.loading = true;
		$http.get("/dashboard/api/block_stats/?start="+start_time+"&end="+end_time+"&chart_type=bar")
		.success(function(data){
			var blockChartInfo= data.objects;
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			$scope.highchartsNG = {
				chart: {
					type: blockChartInfo.chart_type,
					margin: [5, 10, 5, 5]
				},
				title: {
					text: ''
				},
				subtitle: {
					text: 'تعداد بلاک '
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد بلاک ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست <br/>'
				},
				series: [{
					name: 'blocks',
					data: blockChartInfo.data,
					marker: {
						symbol: 'circle',
					},
					color: '#7EB6EC'
				}]
			}
		}).finally(function () {
			$scope.loading = false;
		});
	};
	$scope.refresh_blocks();
}]);

app.controller('userCtrl',['$scope','$http', function($scope, $http) {
	$scope.refresh_users = function(){
		var start_time = $( "#user_start_value" ).val();
		var end_time = $( "#user_end_value" ).val();
		$scope.loading = true;
		$http.get("/dashboard/api/user_stats/?start="+start_time+"&end="+end_time+"&chart_type=bar")
		.success(function(data){
			var userChartInfo= data.objects;
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			$scope.highchartsNG = {
				chart: {
					type: userChartInfo.chart_type
				},
				title: {
					text: ''
				},
				subtitle: {
					text: 'تعداد کاربر '
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد کاربر ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست <br/>'
				},
				series: [{
					name: 'users',
					data: userChartInfo.data,
					marker: {
						symbol: 'circle',
					},
					color: '#7EB6EC'
				}]
			}
		}).finally(function () {
			$scope.loading = false;
		});
	};
	$scope.refresh_users();
}]);

app.controller('followCtrl',['$scope','$http', function($scope, $http) {
	$scope.refresh_follows = function() {
		var start_time = $( "#follow_start_value" ).val();
		var end_time = $( "#follow_end_value" ).val();
		$scope.loading = true;
		$http.get('/dashboard/api/follow_stats/?start='+start_time+'&end='+end_time+'&chart_type=line')
		.success(function(data){
			var folowChartInfo= data.objects;
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			$scope.highchartsNG = {
				chart: {
					type: folowChartInfo.chart_type,
					spacingTop: 3,
					spacingRight: 0,
					spacingBottom: 3,
					spacingLeft: 0
				},
				credits: {
					enabled: false
				},
				title: {
					text: ''
				},
				subtitle: {
					text: 'تعداد فالو'
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد فالو ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b style="direction:ltr;">52 785{point.y}</b> پست <br/>'
				},
				series: [{
					name: 'follows',
					data: folowChartInfo.data,
					marker: {
						symbol: 'circle',
					},
					color: '#7EB6EC'
				}]
			};
		}).finally(function () {
			$scope.loading = false;
		});
	};

	$scope.refresh_follows();
}]);

app.controller('likesCtrl',['$scope','$http', function($scope, $http) {

	$scope.refresh_likes=function(){
		var start_time = $( "#like_start_value" ).val();
		var end_time = $( "#like_end_value" ).val();
		$scope.loading = true;
		$http.get("/dashboard/api/like_stats/?start="+start_time+"&end="+end_time+"&chart_type=line")
		.success(function(data){
			var likesChartInfo= data.objects;
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			$scope.highchartsNG = {
				
				chart: {
					type: likesChartInfo.chart_type
				},
				title: {
					text: ''
				},
				subtitle: {
					text: 'تعداد لایک'
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد لایک ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b style="direction:ltr;">52 785{point.y}</b> پست <br/>'
				},
				series: [{
					name: 'likes',
					data: likesChartInfo.data,
					marker: {
						symbol: 'circle',
					},
					color: '#7EB6EC'
				}]
			}
		}).finally(function () {
			$scope.loading = false;
		})
	};
	$scope.refresh_likes();
}]);

app.controller('commentCtrl',['$scope','$http', function($scope, $http) {
	$scope.refresh_comments=function(){
		var start_time = $( "#comment_start_value" ).val();
		var end_time = $( "#comment_end_value" ).val();
		$scope.loading = true;
		$http.get("/dashboard/api/comment_stats/?start="+start_time+"&end="+end_time+"&chart_type=line")
		.success(function(data){
			var cmChartInfo= data.objects;
			Highcharts.setOptions({
				global: {
					useUTC: false
				}
			});
			$scope.highchartsNG = {
				chart: {
					type: cmChartInfo.chart_type
				},
				title: {
					text: ''
				},
				subtitle: {
					text: 'تعداد نظرات های '
				},
				xAxis: { type: 'datetime' },
				yAxis: {
					title:{
						text: "تعداد نظرات ها"
					}

				},
				tooltip: {
					headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
					pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y}</b> پست <br/>'
				},
				series: [{
					name: 'comments',
					data: cmChartInfo.data,
					marker: {
						symbol: 'circle',
					},
					color: '#7EB6EC'
				}]
			}
		}).finally(function () {
			$scope.loading = false;
		});
	};
	$scope.refresh_comments();
}]);

/****** end user activity *******/

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
