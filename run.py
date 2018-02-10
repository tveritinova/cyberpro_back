from werkzeug.contrib.fixers import ProxyFix
from app import create

app = create()
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run(debug=True)