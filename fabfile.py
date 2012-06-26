
import os
from fabric.api import local, env
from fabric.contrib.project import rsync_project

env.hosts = [ 'plug.grambo.me.uk' ]
env.user = 'resumr'


def coffeescript():
    local( 'coffee -o static/js -c coffeescript' )


def less():
    args = [
            os.path.join( 'static', 'less', x )
            for x in ( 'style.less', 'style.css' )
            ]
    local( 'lessc {0} {1}'.format( *args ) )


def build():
    coffeescript()
    less()
    local( 'r.js -o app.build.js' )
    # TODO: Remmove un-needed .js files from build
    pass


def deploy():
    # TODO: Might be decent to run tests before deploying?
    excludes = [
            '.pyc', '.git', 'config.py', 'data',
            'syncplug.sh' 'fabfile.py'
            ]
    rsync_project( '/home/resumr/app', 'build/', exclude=excludes )
