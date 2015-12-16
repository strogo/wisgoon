var app = angular.module('myApp', ['ui.router','infinite-scroll','wu.masonry']);

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
     
 });