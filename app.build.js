({
    appDir: './',
    baseUrl: 'static/js/',
    dir: 'build/',
    mainConfigFile: 'static/js/main.js',
    fileExclusionRegExp: /(^\.)|(\.less$)|(\.pyc$)|(^data)|(^build)|(tests)/,
    modules: [
        {
            name: 'main'
        },
        {
            name: 'app'
        }
    ]
})
