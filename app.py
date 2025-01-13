from flask import Flask
from views import views
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__,template_folder = "templates", static_folder = "static")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.config['DB'] = db

app.register_blueprint(views,url_prefix = "/views")


if __name__ == "__main__": 
    app.app_context().push()
    app.run(debug = True, port = 8000)