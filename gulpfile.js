var gulp        = require('gulp');
var browserSync = require('browser-sync').create();
var sass        = require('gulp-sass');
var minifyCss   = require('gulp-minify-css');
var reload      = browserSync.reload;


gulp.task('templates', function() {
    return gulp.src('./pin/templates/**/*.html')
    .pipe(browserSync.stream());
});


gulp.task('minify-css', function() {
    return gulp.src('./feedreader/media/v2/css_org/*.css')
    .pipe(minifyCss({compatibility: 'ie8'}))
    .pipe(gulp.dest('./feedreader/media/v2/css'));
});

gulp.task('minify-css-shop', function() {
    return gulp.src('./feedreader/media/shop/css_org/*.css')
    .pipe(minifyCss({compatibility: 'ie8'}))
    .pipe(gulp.dest('./feedreader/media/shop/css'));
});

gulp.task('css', function() {
    return gulp.src("./feedreader/media/v2/css")
    .pipe(browserSync.stream());
});

gulp.task('css-shop', function() {
    return gulp.src("./feedreader/media/shop/css")
    .pipe(browserSync.stream());
});
gulp.task('sass', function () {
    gulp.src('./feedreader/media/v2/scss/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./feedreader/media/v2/css'));
});

gulp.task('sass:watch', function () {
    gulp.watch('./feedreader/media/v2/scss/*.scss', ['sass']);
});

gulp.task('default', ['css', 'css-shop', 'minify-css', 'minify-css-shop'], function() {
// gulp.task('default', ['sass', 'css', 'minify-css', 'templates'], function() {

    browserSync.init({
        proxy: "0.0.0.0:8000"
    });

    gulp.watch("./feedreader/media/v2/css_org/*.css", ['minify-css', 'css']);
    gulp.watch("./feedreader/media/v2/css/*.css", ['css']);
    gulp.watch("./feedreader/media/shop/css_org/*.css", ['minify-css-shop', 'css-shop']);
    gulp.watch("./feedreader/media/shop/css/*.css", ['css-shop']);
    // gulp.watch("./pin/templates/**/*.html", ['templates']);

});

