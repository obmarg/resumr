import markdown
import shutil
import sys
from flask import Flask, render_template
from flask import redirect, url_for
from services import GetAuthService, SERVICES_AVALIABLE
from utils.markdownutils import CleanMarkdownOutput
import utils.viewutils
from utils.viewutils import IsLoggedIn, GetDoc
from views.api import SectionApi, StylesheetApi
from views import AuthViews, SystemTestViews

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


class ResumrApp(Flask):
    def __init__(self):
        super( ResumrApp, self ).__init__(__name__)

        self.config.from_object(DefaultConfig)
        self.config.from_envvar('RESUMR_CONFIG', silent=True)
        utils.viewutils.SetConfig(self.config)

        # Set up the services
        oAuthUrl = 'http://' + self.config[ 'SERVER_NAME' ] + '/login/auth/{0}'
        for name in SERVICES_AVALIABLE:
            GetAuthService(
                    name, self.config,
                    oAuthUrl.format( name )
                    )

    def SystemTestMode(self):
        # Called to activate system test mode for use w/ cucumber
        app.regsister_blueprint(SystemTestViews, url_prefix='/systemtest')
        self.config[ 'SERVER_NAME' ] = '127.0.0.1:{0}'.format(
                SYSTEMTEST_PORT
                )
        self.config[ 'DEBUG' ] = True
        self.config[ 'SYSTEM_TEST' ] = True
        self.config[ 'DATA_PATH' ] = 'systemtestdata'
        self.SystemTestReset()

    def SystemTestReset(self):
        shutil.rmtree( app.config[ 'DATA_PATH' ], ignore_errors=True )
        self.config[ 'BYPASS_LOGIN' ] = True


app = ResumrApp()
app.register_blueprint(AuthViews)
app.register_blueprint(SectionApi, url_prefix='/api/sections')
app.register_blueprint(StylesheetApi, url_prefix='/api/stylesheet')


@app.route("/")
def index():
    if IsLoggedIn():
        return render_template('index.html')
    return redirect( url_for( 'auth.Login' ) )

#############
#
# Misc routes
#
#############


@app.route('/render')
def Render():
    if not IsLoggedIn():
        return redirect( url_for( 'auth.Login' ) )
    d = GetDoc()
    Convert = lambda x: CleanMarkdownOutput(markdown.markdown(x))
    sections = [(s.name, s.CurrentContent()) for i, s in d.CurrentSections()]
    output = [
            dict(name=name, content=Convert(content))
            for name, content in sections
            ]

    return render_template(
            'render.html',
            sections=output,
            stylesheet=d.GetStylesheet().CurrentContent()
            )


if __name__ == "__main__":
    args = {}
    if len( sys.argv ) > 1:
        if sys.argv[1] == 'systemtest':
            print "Running in system test mode"
            args['port'] = SYSTEMTEST_PORT
            app.SystemTestMode()
    app.run(**args)
