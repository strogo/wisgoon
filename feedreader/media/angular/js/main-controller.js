'use strict';
app.controller('mainController',['$scope', '$stateParams','$http', function($scope,$stateParams, $http) {
	$scope.username = user_username;
	$scope.avatar = user_avatar;
}]);

app.controller('catController',['$http','$scope','$stateParams', function($http,$scope,$stateParams, categoryItems) {
	var categoryItems = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "http://127.0.0.1:8000/api/v6/post/category/"+$stateParams.cat_id+"/?token="+user_token;
	};

	categoryItems.prototype.nextPage = function() {
		if (this.busy) return;
		this.busy = true;
		$http.get(this.url).success(function(data) {
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
	if (!user_token) {
		return
	};
	$http.get("http://127.0.0.1:8000/api/v6/category/all/?token="+user_token)
	.success(function(data){
		$scope.catItems = data.objects;
	});
	$scope.brickItem = new categoryItems();
}]);

app.controller('postController',['$scope','$http','$stateParams', function($scope,$http,$stateParams,related) {	
	$scope.sendCommentForm = function() {
		$http({
			method  : 'POST',
			data    : $.param($scope.formData), 
			url     : 'http://127.0.0.1:8000/api/v6/comment/add/post/'+$stateParams.post_id+'/?token='+user_token,
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})
		.success(function(data) {
			console.log("comment sent");
		})
	};
	$http.get("http://127.0.0.1:8000/api/v6/comment/showComments/post/"+$stateParams.post_id+"/?token="+user_token)
	.success(function(data){
		$scope.comments = data.objects;
	});

	$http.get("http://127.0.0.1:8000/api/v6/like/likers/post/"+$stateParams.post_id+"/")
	.success(function(data){
		$scope.likers = data.post_likers.objects;
	});

	$scope.deleteCommentForm = function(cmId) {
		$http.get("http://127.0.0.1:8000/api/v6/comment/delete/"+cmId+"/?token="+user_token)
		.success(function(data){
			console.log("deleted");
		});

	};

	$http.get("http://127.0.0.1:8000/api/v6/post/item/"+$stateParams.post_id+"/?token="+user_token)
	.success(function(data){
		$scope.post = data;
	});

	$scope.report= function(){
		$http.get("http://127.0.0.1:8000/api/v6/post/report/"+$stateParams.post_id+"/?token="+user_token)
		.success(function(data){
			console.log("reported");
		});
	};

	$scope.likePost = function() {
		$http({
			method  : 'GET',
			url     : 'http://127.0.0.1:8000/api/v6/like/post/'+$stateParams.post_id+'/?token='+user_token,
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})
		.success(function(data) {
			$scope.post=data;
		})
	};
	
	$scope.editPostForm = function() {
		$http({
			method  : 'POST',
			url     : 'http://127.0.0.1:8000/api/v6/post/edit/'+$stateParams.post_id+'/?token='+user_token,
			data    : $.param($scope.formData), 
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})
		.success(function(data) {
			$location.path('/');
			console.log(data);
		});
	};

	var related = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "http://127.0.0.1:8000/api/v6/post/related/"+$stateParams.post_id+"/";
	};

	related.prototype.nextPage = function() {
		if (this.busy) return;
		this.busy = true;
		$http.get(this.url).success(function(data) {
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

	$scope.brickItem = new related();
}]);

app.controller('searchPostController',['$scope','$stateParams','$http','$location',function($scope,$stateParams,$http,$location) {

	$scope.showSearchPost = function() {
		console.log("show searh post initialized");
		this.bricks = [];
		this.busy = false;
		this.after = '';
		$stateParams.s_query=this.query;
		this.url = "http://wisgoon.com/api/v6/post/search/?q="+$stateParams.s_query;
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

app.controller('profileController',['$scope','$location','$stateParams', '$http', function($scope,$location, $stateParams,$http ,userPosts) {

	var userPosts = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		if ($stateParams.user_profile_id.length == 0){
			$stateParams.user_profile_id =user_id ;
			$scope.profile_userId = user_id;
		}else{
			$scope.profile_userId = $stateParams.user_profile_id;
		}
		this.url = "http://127.0.0.1:8000/api/v6/post/user/"+$stateParams.user_profile_id+"/";
		$http.get("http://127.0.0.1:8000/api/v6/auth/user/"+$stateParams.user_profile_id+"/")
		.success(function(data){
			$scope.profile_info = data;
			$scope.formData = data;
		});
		$http.get("http://127.0.0.1:8000/api/v6/auth/followers/"+$stateParams.user_profile_id+"?token="+user_token)
		.success(function(data){
			$scope.followers=data.objects;
		});

		$http.get("http://127.0.0.1:8000/api/v6/auth/following/"+$stateParams.user_profile_id+"?token="+user_token)
		.success(function(data){
			$scope.followings=data.objects;
		});
	};

	userPosts.prototype.nextPage = function() {

		if (this.busy) return;
		this.busy = true;
		$http.get(this.url).success(function(data) {
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

	$scope.brickItem = new userPosts();

	$scope.follow= function(){

		$http.get("http://127.0.0.1:8000/api/v6/auth/follow/?token="+user_token+"&user_id="+$stateParams.user_profile_id)
		.success(function(data){
			console.log(data);
		})
	};
	$scope.unfollow= function(){

		$http.get("http://127.0.0.1:8000/api/v6/auth/unfollow/?token="+user_token+"&user_id="+$stateParams.user_profile_id)
		.success(function(data){
			console.log(data);
		})
	};
	$scope.editProfileForm = function() {
		$http({
			method  : 'POST',
			url     : 'http://127.0.0.1:8000/api/v6/auth/user/update/?token='+user_token,
			data    : $.param($scope.formData), 
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})
		.success(function(data) {
			$scope.editPost= data;
			$location.path('/post');
			console.log(data);
		});
	};
}]);

app.controller('latestController',['$http','$scope', function($http, $scope, latest) {


	var latest = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "http://127.0.0.1:8000/api/v6/post/latest/";
	};

	latest.prototype.nextPage = function() {
		if (this.busy) {
			return;
		}
		this.busy = true;

		$http.get(this.url).success(function(data) {
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

	$scope.brickItem = new latest();
}]);

app.controller('EditorpostController',['$scope','$http', function($scope, $http, editorPost) {

	var editorPost = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "http://127.0.0.1:8000/api/v6/post/choices/";
	};

	editorPost.prototype.nextPage = function() {
		if (this.busy) return;
		this.busy = true;
		$http.get(this.url).success(function(data) {
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

	$scope.brickItem = new editorPost();
}]);

app.controller('likedpostController',['$scope','$http', function($scope, $http, likedPost) {

	var likedPost = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "http://127.0.0.1:8000/api/v6/auth/user/"+user_id+"/likes/";
	};

	likedPost.prototype.nextPage = function() {
		if (this.busy) return;
		this.busy = true;
		$http.get(this.url).success(function(data) {
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

	$scope.brickItem = new likedPost();
}]);

app.controller('friendspostController',['$scope','$http', function($scope, $http, friendsPost) {

	var friendsPost = function() {
		this.bricks = [];
		this.busy = false;
		this.after = '';
		this.url = "http://127.0.0.1:8000/api/v6/post/friends/?token="+user_token;
	};

	friendsPost.prototype.nextPage = function() {
		if (this.busy) return;
		this.busy = true;
		$http.get(this.url).success(function(data) {
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

	$scope.brickItem = new friendsPost();
}]);

app.controller('loginController',function($scope,$http,$location,$state) {

	$scope.loginFormValidat = function() {
		$http({
			method  : 'POST',
			url     : 'http://127.0.0.1:8000/api/v6/auth/login/',
			data    : $.param($scope.formData), 
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		}) .success(function(data) {
			$scope.message = data.message;
			$scope.showSuccess = true;
			$location.path('/');
		})
		.error(function(data) {      
			$scope.errorName = data.message;
			$scope.showError = true;

		});
	};
});

app.controller('registerController',function($scope, $http,$location){

	$scope.registerationForm = function() {
		$http({
			method  : 'POST',
			url     : 'http://127.0.0.1:8000/api/v6/auth/register/',
			data    : $.param($scope.formData), 
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})
		.success(function(data) {
			$location.path('/login');
		})
	};
});

app.controller('logoutController',function($scope,$http,$location){
	$scope.logout = function() {
		$http.get("http://127.0.0.1:8000/api/v6/auth/logout/")
		.success(function(data) {
			user_token='';
			user_id='';
			$location.path('/');
		})
	};
});

app.controller('sendPostController', ['$scope','$http','$location','fileUpload',function($scope,$http,$location,fileUpload){

	$scope.sendPost = function() {
		$http({
			method  : 'POST',
			url     : 'http://127.0.0.1:8000/api/v6/post/send/?token='+user_token,
			data    : $.param($scope.formData), 
			headers : { 'Content-Type': 'application/x-www-form-urlencoded' }
		})
		.success(function(data) {
			$location.path('/');
			console.log(data);
		});
	};

	var file = $scope.myFile;
	console.log('file is ' );
	var uploadUrl = 'http://127.0.0.1:8000/api/v6/post/send/?token='+user_token;
	fileUpload.uploadFileToUrl(file, uploadUrl);
}]);

app.directive('fileModel', ['$parse', function ($parse) {
	return {
		restrict: 'A',
		link: function(scope, element, attrs) {
			var model = $parse(attrs.fileModel);
			var modelSetter = model.assign;

			element.bind('change', function(){
				scope.$apply(function(){
					modelSetter(scope, element[0].files[0]);
				});
			});
		}
	};
}]);

app.service('fileUpload', ['$http', function ($http) {
	this.uploadFileToUrl = function(file, uploadUrl){
		var fd = new FormData();
		fd.append('file', file);
		$http.post(uploadUrl, fd, {
			transformRequest: angular.identity,
			headers: {'Content-Type': undefined}
		})
		.success(function(){
		})
		.error(function(){
		});
	}
}]);

app.controller('notifController',function($scope,$http,$location){
	if (!user_token) {
		return
	};
	$http.get("http://127.0.0.1:8000/api/v6/notif/count/?token="+user_token)
	.success(function(data){
		$scope.notifCount=data;
	});

	$http.get("http://127.0.0.1:8000/api/v6/notif/?token="+user_token)
	.success(function(data){
		$scope.notifs=data.objects;
	});
});


