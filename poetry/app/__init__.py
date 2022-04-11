from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import logging, os, datetime

app = Flask(__name__, instance_relative_config=True, template_folder="templates")
app.config.from_object('app.config')
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

CORS(app, resources=r'/*')

if os.path.exists('./logs'):
    if os.path.isdir('./logs'):
        print('./logs is exists!')
    else:
        os.mkdir('./logs')
else:
    os.mkdir('./logs')

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("./logs/log"+str(datetime.datetime.now().strftime('%Y-%m-%d'))+".txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(console)


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def register_bp(app):
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


def create_app():
    db.init_app(app)
    # login_manager.init_app(app)
    register_bp(app)

    return app
