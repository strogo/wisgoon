'use strict';
var app = angular.module('myApp', ['ui.router','highcharts-ng','infinite-scroll','wu.masonry']);

app.config(function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[{');
  $interpolateProvider.endSymbol('}]}');
});

app.config(function ($stateProvider, $urlRouterProvider,$sceProvider) {
     // For any unmatched url, send to /route1
     $sceProvider.enabled(false);
     $urlRouterProvider.otherwise("/");
     $stateProvider
     .state('home', {
      url: "/",
      templateUrl: static_cdn + "dashboard/html/home.html?q=2",
      controller: "indexController"
    })
     .state('ads', {
      url: "/ads",
      templateUrl: static_cdn + "dashboard/html/post/ads.html",
      controller: "adsController"
    })
     .state('logs', {
      url: "/logs",
      templateUrl: static_cdn + "dashboard/html/post/logs.html",
      controller: "logsController"
    })
     .state('userActivity', {
      url: "/userActivity",
      templateUrl: static_cdn + "dashboard/html/post/user_activity.html",
      controller: "activityUserController"
    })
     .state('categoreis', {
      url: "/categoreis",
      templateUrl: static_cdn + "dashboard/html/post/categories.html",
      controller: "catstatController"
    })
     .state('reported', {
      url: "/reported",
      templateUrl: static_cdn + "dashboard/html/post/reported.html",
      controller: "reportedController"
    })
     .state('check_p', {
      url: "/check_p",
      templateUrl: static_cdn + "dashboard/html/post/check_p.html",
      controller: "checkpController"
    })
     .state('new_report', {
      url: "/new_report",
      templateUrl: static_cdn + "dashboard/html/post/new_report.html",
      controller: "reportedController"
    })
     .state('permissionDenied', {
      url: "/permissionDenied",
      templateUrl: static_cdn + "dashboard/html/permissionDenied.html",
      controller: "indexController"
    })
     .state('searchUser', {
      url: "/searchUser",
      templateUrl: static_cdn + "dashboard/html/post/searchUser.html",
      controller: "searchController"
    })
     
   });
app.directive('ngReallyClick', [function() {
  return {
    restrict: 'A',
    link: function(scope, element, attrs) {
      element.bind('click', function() {
        var message = attrs.ngReallyMessage;
        if (message && confirm(message)) {
          scope.$apply(attrs.ngReallyClick);
        }
      });
    }
  }
}]);