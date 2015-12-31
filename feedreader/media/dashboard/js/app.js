'use strict';
var app = angular.module('myApp', ['ui.router','highcharts-ng','infinite-scroll','wu.masonry']);

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
        templateUrl: "http://127.0.0.1:8000/media/dashboard/html/home.html",
        controller: "indexController"
    })
     .state('ads', {
        url: "/ads",
        templateUrl: "http://127.0.0.1:8000/media/dashboard/html/post/ads.html",
        controller: "adsController"
    })
     .state('logs', {
        url: "/logs",
        templateUrl: "http://127.0.0.1:8000/media/dashboard/html/post/logs.html",
        controller: "logsController"
    })
     .state('userActivity', {
        url: "/userActivity",
        templateUrl: "http://127.0.0.1:8000/media/dashboard/html/post/user_activity.html",
        controller: "activityUserController"
    })
     .state('categoreis', {
        url: "/categoreis",
        templateUrl: "http://127.0.0.1:8000/media/dashboard/html/post/categories.html",
        controller: "catstatController"
    })
     .state('reported', {
        url: "/reported",
        templateUrl: "http://127.0.0.1:8000/media/dashboard/html/post/reported.html",
        controller: "reportedController"
    })
     
 });