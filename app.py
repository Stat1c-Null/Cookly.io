from flask import Flask
from views import views
from config import DB

def create_app():
    app = Flask(__name__,template_folder = "templates", static_folder = "static")

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CooklyDB.db'
    app.secret_key = "test"

    DB.init_app(app)

    app.register_blueprint(views,url_prefix = "/views")

    return app
if __name__ == "__main__": 
    app = create_app()
    with app.app_context():
        DB.create_all()

    app.run(debug = True, port = 8000)