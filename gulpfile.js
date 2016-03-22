var gulp = require('gulp');
var coffee = require('gulp-coffee');
var uglify = require('gulp-uglify');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var rename = require('gulp-rename');
var autoprefixer = require('gulp-autoprefixer');
var watch = require('gulp-watch');
var plumber = require('gulp-plumber');
var react = require('gulp-react');
var webpack = require('webpack-stream');
var babel = require('gulp-babel');
var named = require('vinyl-named');

gulp.task('default', ['js_now', 'sass_now', 'react', 'js', 'sass']);


gulp.task('react', function () {
    watch(['./savings_champion/resources/js/thb_tool/**/*.jsx'], function () {
        return gulp.start('react_thb');
    });
    watch(['./savings_champion/resources/js/rate_tracker/src/**/*.js'], function () {
        return gulp.start('react_ratetracker');
    })
});

gulp.task('react_thb', function () {
    return gulp.src('./savings_champion/resources/js/thb_tool/*.jsx')
        .pipe(plumber())
        .pipe(named())
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(webpack({
            output: {
                path: __dirname + '/',
                publicPath: "/static/js/thb_tool/",
                filename: '[name].min.js'
            },
            module: {
                loaders: [
                    {
                        test: /\.jsx?$/,
                        exclude: /(node_modules|bower_components)/,
                        loader: 'babel-loader',
                        query: {
                            presets: ['react', 'es2015']
                        }
                    },
                    {test: /\.woff$/, loader: "url-loader?limit=10000&minetype=application/font-woff"},
                    {test: /\.ttf$/, loader: "file-loader"},
                    {test: /\.eot$/, loader: "file-loader"},
                    {test: /\.svg$/, loader: "file-loader"}
                ]
            },
            resolve: {
                extensions: ['', '.js', '.jsx']
            }
        }))
        .pipe(react())
        .pipe(uglify())
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('./savings_champion/resources/js/thb_tool'))
});

gulp.task('react_ratetracker', function () {
    return gulp.src('./savings_champion/resources/js/rate_tracker/src/app.js')
        .pipe(plumber())
        .pipe(named())
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(webpack({
            output: {
                path: __dirname + '/',
                publicPath: "/static/js/rate_tracker/",
                filename: '[name].js'
            },
            module: {
                loaders: [
                    {
                        test: /\.js$/,
                        exclude: /(node_modules|bower_components)/,
                        loader: 'babel-loader',
                        query: {
                            presets: ['react', 'es2015'],
                            plugins: ['transform-runtime']
                        }
                    },
                    {test: /\.woff$/, loader: "url-loader?limit=10000&minetype=application/font-woff"},
                    {test: /\.ttf$/, loader: "file-loader"},
                    {test: /\.eot$/, loader: "file-loader"},
                    {test: /\.svg$/, loader: "file-loader"}
                ]
            },
            resolve: {
                extensions: ['', '.js', '.jsx']
            }
        }))
        .pipe(react())
        //.pipe(uglify())
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest('./savings_champion/resources/js/rate_tracker/dist/'))
});

gulp.task('js', function(){
   watch('./savings_champion/resources/js/**/*.coffee', function() {
       return gulp.start('js_now');
   })
});

gulp.task('js_now', function() {
   return gulp.src('./savings_champion/resources/js/**/*.coffee')
       .pipe(plumber())
       .pipe(sourcemaps.init({loadMaps: true}))
       .pipe(coffee())
       .pipe(sourcemaps.write('./'))
       .pipe(gulp.dest('./savings_champion/resources/js'))
});

gulp.task('sass', function(){
   watch('./savings_champion/resources/sass/**/*.scss', function() {
       return gulp.start('sass_now');
   })
});

gulp.task('sass_now', function() {
   return gulp.src('./savings_champion/resources/sass/**/*.scss')
       .pipe(plumber())
       .pipe(sourcemaps.init({loadMaps: true}))
       .pipe(sass())
       .pipe(autoprefixer())
       .pipe(sourcemaps.write('./'))
       .pipe(gulp.dest('./savings_champion/resources/css'))
});
