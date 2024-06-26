from flask import Blueprint
from controllers import UserController
from flask_jwt_extended import jwt_required

user_router = Blueprint("api user", __name__)
user_controller = UserController()


@user_router.get("/ez-link/v1/avatar/<int:user_id>/<string:profile_name>")
async def get_avatar(user_id, profile_name):
    return await user_controller.get_avatar(user_id, profile_name)


@user_router.post("/ez-link/v1/me")
@jwt_required()
async def get_me():
    return await user_controller.get_me()
