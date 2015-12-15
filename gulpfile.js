var gulp        = require('gulp');
var browserSync = require('browser-sync').create();
var reload      = browserSync.reload;

// gulp.task('serve', function () {

//     browserSync.init({
//         proxy: "0.0.0.0:8000"
//     });

//     gulp.task(default, ['css'], browserSync.reload);
// });

// gulp.watch("feedreader/media/v2/css/*.css").on('change', browserSync.reload);
gulp.task('templates', function() {
    return gulp.src('./pin/templates/**/*.html')
    .pipe(browserSync.stream());
});

gulp.task('css', function() {
    return gulp.src("feedreader/media/v2/css")
    .pipe(browserSync.stream());
});

gulp.task('default', ['css', 'templates'], function() {

    browserSync.init({
        proxy: "0.0.0.0:8000"
    });

    gulp.watch("./feedreader/media/v2/css/*.css", ['css']);
    // gulp.watch("./feedreader/media/v2/css/*.css").on('change', browserSync.stream());
    gulp.watch("./pin/templates/**/*.html", ['templates']);
    // gulp.watch("./pin/templates/**/*.html").on('change', browserSync.stream());

});
