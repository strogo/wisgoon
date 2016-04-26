'use strict';
var aaa = {};

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

app.controller('checkpController',['$scope','$interval','$http', function($scope, $interval, $http ) {

	var msg ;
	$interval(function(){
		if (msg !== a){
			msg = a;
			$http.get("/dashboard/api/home/")
			.success(function(data){
				$scope.indexInfo=data.objects;
			})
		}
	},1000);

	$scope.$on("viewContentLoaded",function(){
		clearInterval(a);

	});


}]);

app.controller('reportedController',['$http' ,'$scope', function($http, $scope) {

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
			data    :  'post_ids='+ cmId,
			url     : '/dashboard/api/delete/post/new',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}).success(function(data) {
		});

		$( "[postId='"+cmId+"']").remove();
	};

	$scope.undoPost = function(cmId) {

		$http({
			method  : 'POST',
			data    : 'post_ids='+ cmId,
			url     : '/dashboard/api/posts/undo/report/new',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		});
		$( "[postId='"+cmId+"']").remove();
	};
	$scope.userInfo = function(cmId) {

		$http.get('/dashboard/api/post/user/'+cmId+'/').success(function(data){
			$scope.userData = data;
		});
	};

	$scope.reported = function() {
		$scope.loading = true;
		$http.get('/dashboard/api/posts/new/report').success(function(data){
			$scope.bricks = data;
		}).finally(function () {
			$scope.loading = false;
		});
	};
	$scope.imeiList = function(iL) {
		$http.get('/dashboard/api/user/imei/'+iL+'/').success(function(data){
			$scope.imeilListItems = data.objects;
		});
	};

	$scope.showReportersModal = function(reporters){
		$scope.modalBrickReportrs =  reporters;
		$("#userInfo").modal("show");
	}

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
	$scope.reported();
}]);

app.controller('catstatController',['$http','$scope', function($http, $scope) {
	$scope.refresh_cat=function(){
		var start_time = $( "#cat_start_value" ).val();
		var end_time = $( "#cat_end_value" ).val();
		var statusSm = 0;
		$http.get("/dashboard/api/post/subcategory/chart/?start_date="+start_time+"&end_date="+end_time)
		.success(function(data){
			var chartInfo= data.objects;

			$('#container').highcharts({
				chart: {
					type: 'pie'
				},
				title: {
					text: 'دسته بندی ها '
				},
				xAxis: {
					type: 'category'
				},

				legend: {
					enabled: true
				},

				plotOptions: {
					pie: {
						allowPointSelect: true,
						cursor: 'pointer',
						dataLabels: {
							enabled: false
						},
						showInLegend: true
					},
					series: {
						borderWidth: 0,
						dataLabels: {
							enabled: true
						},
						point: {
							events: {
								click: function(event) {
									if (statusSm<1) {
										var chart = this.series.chart;
										var name = this.name;
										$http.get("/dashboard/api/post/category/chart/"+name+"/?start_date="+start_time+"&end_date="+end_time)
										.success(function(data){
											swapSeries(chart,name,data);
										});
									};

								}
							}
						}
					}
				},

				series: [{
					name: "دسته بندی",
					colorByPoint: true,
					data: chartInfo
				}]
			});
			var swapSeries = function (chart, name, data) {
				statusSm += 1;
				console.log(statusSm);
				chart.series[0].remove();
				chart.addSeries({
					data: data.objects,
					name: name,
					colorByPoint: true
				});
			}

			$scope.iniChart=function(){
				$scope.refresh_cat();
			};
		});
};
$scope.refresh_cat();
}]);


app.controller('searchController',function($scope,$http,$stateParams,$location) {
	$scope.formData = {}
	aaa= $scope;
	$scope.banImei = function() {
		var postData = {
			description3 : $scope.formData.description3,
			imei : $scope.searchInfo.profile.imei,
			status : !$scope.formData.status
		}
		
		$http({
			method  : 'POST',
			data    :  $.param(postData),
			url     : '/dashboard/api/user/bannedImei/',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}).success(function(data){
			$scope.searchInfo.profile.imei_status = data.imei_status;
		});
	};

	$scope.activeUser = function() {

		var data = {
			description1 : $scope.formData.description1,
			activeId : $scope.formData.activeId,
			activeStatus : !$scope.formData.activeStatus
		}

		$http({
			method  : 'POST',
			url     : '/dashboard/api/user/changeStatus/',
			data    : $.param(data), 
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}) .success(function(data) {
			$scope.searchInfo.profile.user_active = data.profile.user_active;
			console.log(data.profile.user_active);
		});
	};	

	$scope.banProfile = function() {

		var data = {
			description2 : $scope.formData.description2,
			profileBanId : $scope.formData.profileBanId,
			profileBanstatus : !$scope.formData.profileBanstatus
		}
		$http({
			method  : 'POST',
			data    :  $.param(data),
			url     : '/dashboard/api/user/bannedProfile/',
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}).success(function(data){
			$scope.searchInfo.profile.userBanne_profile = data.profile.userBanne_profile;
		});
	};
	$scope.showSearchUser = function() {
		$scope.statusSearch= " ";
		$scope.imei_text= "imei ندارد.";
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
	$scope.getInfo = function(cmId) {

		$http.get('/dashboard/api/user/details/'+cmId+'/').success(function(data){
			$scope.searchInfo = data.objects;
			$scope.formData.activeStatus = data.objects.profile.user_active;
			$scope.formData.profileBanstatus = data.objects.profile.userBanne_profile;
		}).finally(function () {
			$scope.loading = false;
		});
	};	
	$scope.imeiList = function(iL) {
		$http.get('/dashboard/api/user/imei/'+iL+'/').success(function(data){
			$scope.imeilListItems = data.objects;
		});
	};

});

app.controller('adsController',['$scope','$http', function($scope, $http) {


	$scope.nextPage = function() {
		if (this.busy) return;
		this.busy = true;
		$http.get(this.url).success(function(data) {
			this.url = data.meta.next;
			if (!data.meta.next){
				return;
			}
			var showPosts = data.objects;
			for (var i = 0; i < showPosts.length; i++) {
				this.showPosts.push(showPosts[i]);
			}
			$scope.showPosts = showPosts;
			this.busy = false;
		}.bind(this)).finally(function () {
			$scope.loading = false;
		});
	};



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
							allowPointSelect: true,
							cursor: 'pointer',
							events: {
								click: function (event) {
									$scope.loading = true;
									this.showPosts = [];
									this.busy = false;
									this.after = '';
									this.url = "/dashboard/api/post/showAds/?date="+event.point.x;
									$scope.nextPage.bind(this).call();
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

app.controller('deleteAvatarController',function($scope,$http,$location) {
	$scope.delAvatar = function(uId) {
		$http.get("/dashboard/api/user/removeAvatar/"+uId+"/")
		.success(function(data){
			
		});
	};	
});
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