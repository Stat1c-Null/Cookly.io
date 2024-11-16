from flask import Flask
from views import views

app = Flask(__name__,template_folder = "templates", static_folder = "static")

app.register_blueprint(views,url_prefix = "/views")

if __name__ == "__main__": 
    app.run(debug = True, port = 8000)