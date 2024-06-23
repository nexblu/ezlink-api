from flask import Blueprint
from controllers import UserController

user_router = Blueprint("api user", __name__)
user_controller = UserController()


@user_router.get("/ez-link/v1/avatar/<int:user_id>/<string:profile_name>")
async def get_avatar(user_id, profile_name):
    return await user_controller.get_avatar(user_id, profile_name)
