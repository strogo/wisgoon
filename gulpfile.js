var gulp        = require('gulp');
var browserSync = require('browser-sync').create();
var sass        = require('gulp-sass');
var minifyCss   = require('gulp-minify-css');
var reload      = browserSync.reload;


gulp.task('templates', function() {
    return gulp.src('./pin/templates/**/*.html')
    .pipe(browserSync.stream());
});

gulp.task('css', function() {
    return gulp.src("./feedreader/media/v2/css")
    .pipe(browserSync.stream());
});

gulp.task('minify-css', function() {
    return gulp.src('./feedreader/media/v2/css_org/*.css')
    .pipe(minifyCss({compatibility: 'ie8'}))
    .pipe(gulp.dest('./feedreader/media/v2/css'));
});

gulp.task('sass', function () {
    gulp.src('./feedreader/media/v2/scss/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./feedreader/media/v2/css'));
});

gulp.task('sass:watch', function () {
    gulp.watch('./feedreader/media/v2/scss/*.scss', ['sass']);
});

gulp.task('default', ['sass', 'minify-css', 'css', 'templates'], function() {

    browserSync.init({
        proxy: "0.0.0.0:8000"
    });

    gulp.watch("./feedreader/media/v2/css_org/*.css", ['minify-css', 'css']);
    // gulp.watch("./feedreader/media/v2/css/*.css", ['css']);
    gulp.watch("./pin/templates/**/*.html", ['templates']);

});

