module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        cssmin: {
            target: {
                files: [{
                    expand: true,
                    cwd: './feedreader/media/v2/css_org/',
                    src: ['*.css', '!*.min.css'],
                    dest: './feedreader/media/v2/css',
                }],
                files: [{
                    expand: true,
                    cwd: './feedreader/media/shop/css_org/',
                    src: ['*.css', '!*.min.css'],
                    dest: './feedreader/media/shop/css/',
                }]
            }
        }


    });



    // Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    // Default task(s).
    grunt.registerTask('default', ['cssmin']);

};
