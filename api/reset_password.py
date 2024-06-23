from flask import Blueprint, request
from controllers import ResetPasswordController

reset_router = Blueprint("route reset password", __name__)
reset_password_controller = ResetPasswordController()


@reset_router.route(
    "/ez-link/v1/user/reset/reset-password/<string:token>", methods=["POST", "GET"]
)
async def reset_password(token):
    return await reset_password_controller.get_reset_password(token)


@reset_router.post("/ez-link/v1/user/reset/email-reset-password")
async def email_reset_password():
    data = request.json
    email = data.get("email")
    return await reset_password_controller.reset_password(email)
