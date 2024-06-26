from flask import Blueprint, request
from controllers import AuthController
from flask_jwt_extended import jwt_required

auth_router = Blueprint("api auth", __name__)
auth_controller = AuthController()


@auth_router.post("/ez-link/v1/auth/refresh-token")
@jwt_required(refresh=True)
async def refresh_token():
    return await auth_controller.refresh_token()


@auth_router.get("/ez-link/v1/auth/email-verify/<string:token>")
async def account_active(token):
    return await auth_controller.get_account_active(token)


@auth_router.post("/ez-link/v1/auth/email-verify")
async def account_active_email():
    data = request.json
    email = data.get("email")
    return await auth_controller.email_verify(email)


@auth_router.route(
    "/ez-link/v1/auth/reset/reset-password/<string:token>",
    methods=["POST", "GET"],
)
async def reset_password(token):
    return await auth_controller.get_reset_password(token)


@auth_router.post("/ez-link/v1/auth/reset/email-reset-password")
async def email_reset_password():
    data = request.json
    email = data.get("email")
    return await auth_controller.reset_password(email)


@auth_router.post("/ez-link/v1/auth/login")
async def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    return await auth_controller.login(email, password)


@auth_router.post("/ez-link/v1/auth/register")
async def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    return await auth_controller.register(username, email, password, confirm_password)
