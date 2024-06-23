from flask import Blueprint, request
from controllers import LoginController

login_router = Blueprint("api user login", __name__)
login_controller = LoginController()


@login_router.post("/ez-link/v1/user/login")
async def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    return await login_controller.login(email, password)
