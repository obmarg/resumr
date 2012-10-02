
import markdown
from flask import Blueprint, redirect, url_for, render_template
from utils.markdownutils import CleanMarkdownOutput
from utils.viewutils import IsLoggedIn, GetDoc

app = Blueprint('render', __name__)


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
