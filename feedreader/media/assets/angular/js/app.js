var app = angular.module('wisgoon', ['ui.router','infinite-scroll','wu.masonry']);
// var app = angular.module('wisgoon', ['ui.router','infinite-scroll','wu.masonry','ngMessages']);

app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});

app.config(function ($stateProvider, $urlRouterProvider) {
     // For any unmatched url, send to /route1
     $urlRouterProvider.otherwise("/");
     $stateProvider
     .state('home', {
        url: "/",
        templateUrl: static_cdn + "angular/html/editor-posts.html",
        controller: "EditorpostController"
    })
     .state('register', { 
        url: "/register",
        templateUrl: static_cdn + "angular/html/registration/register.html",
        controller: "registerController"
    })
     .state('login', { 
        url: "/login",
        templateUrl: static_cdn + "angular/html/registration/login.html",
        controller: "loginController"
    })
     
     .state('post', { 
        url: "/post/:post_id",
        templateUrl: static_cdn + "angular/html/post.html",
        controller: "postController"
    })
     .state('friendsPost', { 
        url: "/friendsPost",
        templateUrl: static_cdn + "angular/html/friends-posts.html",
        controller: "friendspostController"
    })
     .state('followingsList', { 
        url: "/followingsList/:user_profile_id",
        templateUrl: static_cdn + "angular/html/followings-list.html",
        controller: "profileController"
    })
     .state('followersList', { 
        url: "/followersList/:user_profile_id",
        templateUrl: static_cdn + "angular/html/followers-list.html",
        controller: "profileController"
    })
     .state('likedPost', { 
        url: "/likedPost",
        templateUrl: static_cdn + "angular/html/liked-post.html",
        controller: "likedpostController"
    })
     .state('notifs', { 
        url: "/notifs",
        templateUrl: static_cdn + "angular/html/all-notifs.html",
        controller: "notifController"
    })
     .state('latest', { 
        url: "/latest",
        templateUrl: static_cdn + "angular/html/latest.html",
        controller: "latestController"
    })
     .state('search', { 
        url: "/search/",
        templateUrl: static_cdn + "angular/html/search.html",
        controller:"searchPostController"
    })
     .state('profile', { 
        url: "/profile/:user_profile_id",
        templateUrl: static_cdn + "angular/html/profile.html",
        controller: "profileController"
    })
     .state('editProfile', { 
        url: "/editProfile/:user_profile_id",
        templateUrl: static_cdn + "angular/html/edit-profile.html",
        controller: "profileController"
    })
     .state('sendPost', { 
        url: "/sendPost",
        templateUrl: static_cdn + "angular/html/send-post.html",
        controller: "sendPostController"
    })
     .state('editPost', { 
        url: "/editPost/:post_id",
        templateUrl: static_cdn + "angular/html/edit-post.html",
        controller: "postController"
    })
     .state('catPost', { 
        url: "/catPost/:cat_id",
        templateUrl: static_cdn + "angular/html/cat-page.html",
        controller: "catController"
    })
     .state('logout', { 
       url: "/logout",
       template:" ",
       controller: "logoutController"

   })
 });
