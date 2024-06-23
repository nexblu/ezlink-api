from flask import Blueprint, request
from controllers import RegisterController

register_router = Blueprint("api user register", __name__)
register_controller = RegisterController()


@register_router.post("/ez-link/v1/user/register")
async def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    return await register_controller.add_user(
        username, email, password, confirm_password
    )
