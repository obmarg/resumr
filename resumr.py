import shutil
import sys
from flask import Flask, render_template
from flask import redirect, url_for
from services import GetAuthService, SERVICES_AVALIABLE
from views.api import SectionApi, StylesheetApi
from views import AuthViews, SystemTestViews, RenderViews
from utils.viewutils import IsLoggedIn

SYSTEMTEST_PORT = 43001


class DefaultConfig(object):
    SERVER_NAME = ''
    SECRET_KEY = ''
    DEBUG = False
    TESTING = False
    FACEBOOK_OAUTH_KEY = ''
    FACEBOOK_OAUTH_SECRET = ''
    GOOGLE_OAUTH_KEY = ''
    GOOGLE_OAUTH_SECRET = ''
    BYPASS_LOGIN = False
    BYPASS_REPO_NAME = 'test'
    DATA_PATH = None
    SYSTEM_TEST = False
    MAX_STYLESHEET_SIZE = 1024 * 512


class SystemTestConfig(DefaultConfig):
    SERVER_NAME = '127.0.0.1:{0}'.format(SYSTEMTEST_PORT)
    DEBUG = True
    SYSTEM_TEST = True
    DATA_PATH = 'systemtestdata'


class ResumrApp(Flask):
    def __init__(self, config_object):
        super( ResumrApp, self ).__init__(__name__)

        self.config.from_object(config_object)
        if config_object.SYSTEM_TEST:
            self.SystemTestReset()
        else:
            self.config.from_envvar('RESUMR_CONFIG', silent=True)

        # Set up the services
        oAuthUrl = 'http://' + self.config['SERVER_NAME'] + '/login/auth/{0}'
        for name in SERVICES_AVALIABLE:
            GetAuthService(
                    name, self.config,
                    oAuthUrl.format( name )
                    )

    def SystemTestReset(self):
        shutil.rmtree(self.config[ 'DATA_PATH' ], ignore_errors=True)
        self.config[ 'BYPASS_LOGIN' ] = True


def MakeApp(systemtest=False):
    app = ResumrApp(SystemTestConfig if systemtest else DefaultConfig)
    app.register_blueprint(AuthViews)
    app.register_blueprint(SectionApi, url_prefix='/api/sections')
    app.register_blueprint(StylesheetApi, url_prefix='/api/stylesheet')
    app.register_blueprint(RenderViews)

    if systemtest:
        app.register_blueprint(SystemTestViews, url_prefix='/systemtest')

    @app.route("/")
    def index():
        if IsLoggedIn():
            return render_template('index.html')
        return redirect( url_for( 'auth.Login' ) )

    return app


if __name__ == "__main__":
    args = {}
    systemtest = False
    if len( sys.argv ) > 1:
        if sys.argv[1] == 'systemtest':
            print "Running in system test mode"
            args['port'] = SYSTEMTEST_PORT
            systemtest = True
    MakeApp(systemtest).run(**args)
