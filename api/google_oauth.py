from flask import Blueprint
from controllers import GoogleOauthController

google_oauth_router = Blueprint("api_google_oauth_login", __name__)
google_oauth_controller = GoogleOauthController()


@google_oauth_router.route("/login/google")
async def login_google():
    return await google_oauth_controller.google_login()


@google_oauth_router.route("/authorize/google")
async def authorize_google():
    return await google_oauth_controller.authorize_google()
