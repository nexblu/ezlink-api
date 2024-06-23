from flask import Flask
from flask_cors import CORS
from config import MONGODB_URL, SECRET_KEY, POSTGRESQL_URL
from database import db_session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from utils import (
    handle_404,
    handle_415,
    handle_429,
    handle_400,
    handle_401,
    handle_403,
    handle_405,
)
from api.register import register_router
from api.login import login_router, login_controller
from api.account_active import account_active_router
from api.refresh_token import refresh_token_router
from api.google_oauth import google_oauth_router, google_oauth_controller
from api.discord_oauth import discord_oauth_router
from api.email import email_router
from api.user import user_router
from api.reset_password import reset_router

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRESQL_URL
CORS(app, supports_credentials=True)
limiter = Limiter(
    get_remote_address, app=app, default_limits=[""], storage_uri=MONGODB_URL
)
app.secret_key = SECRET_KEY
google_oauth_controller.google_oauth.init_app(app)
login_controller.bcrypt.init_app(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.after_request
async def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.teardown_appcontext
async def shutdown_session(exception=None):
    db_session.remove()


@app.teardown_request
async def checkin_db(exception=None):
    db_session.remove()


app.register_blueprint(register_router)
app.register_blueprint(login_router)
app.register_blueprint(account_active_router)
app.register_blueprint(refresh_token_router)
app.register_blueprint(google_oauth_router)
app.register_blueprint(discord_oauth_router)
app.register_blueprint(email_router)
app.register_blueprint(user_router)
app.register_blueprint(reset_router)

app.register_error_handler(429, handle_429)
app.register_error_handler(404, handle_404)
app.register_error_handler(415, handle_415)
app.register_error_handler(400, handle_400)
app.register_error_handler(401, handle_401)
app.register_error_handler(403, handle_403)
app.register_error_handler(405, handle_405)
