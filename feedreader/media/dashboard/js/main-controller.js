'use strict';
app.controller('mainController',['$scope','$http', function($scope, $http) {
	$scope.username = user_username;
	$scope.avatar = user_avatar;
}]);
app.controller('indexController',['$scope','$http', function($scope, $http) {
	$http.get("http://127.0.0.1:8000/dashboard/api/home/")
	.success(function(data){
		console.log(data);
		$scope.indexInfo=data;
	});
}]);
app.controller('adsController',['$scope','$http', function($scope, $http) {

}]);
app.controller('logsController',['$scope','$http', function($scope, $http) {

}]);
app.controller('activityUserController',['$scope','$http', function($scope, $http) {

}]);
app.controller('categoryController',['$scope','$http', function($scope, $http) {

}]);
app.controller('reportedController',['$http' ,'$scope', function($http, $scope, reported) {

$scope.user_token = "12345";
	var reported = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "http://127.0.0.1:8000/dashboard/api/post/reported/";
	};

	reported.prototype.nextPage = function() {
		if (this.busy)
		this.busy = true;

		$http.get(this.url).success(function(data) {
			this.url = data.next;
			if (data.next == " "){
				return;
			}
		console.log("value");
			var bricks = data.posts;
			for (var i = 0; i < bricks.length; i++) {
				this.bricks.push(bricks[i]);
			}
			this.busy = false;
		}.bind(this));
	};

	$scope.postItem = new reported();
}]);