from flask import Blueprint, request
from controllers import RefreshTokenController

refresh_token_router = Blueprint("api refresh token", __name__)
refresh_token_controller = RefreshTokenController()


@refresh_token_router.post("/ez-link/v1/user/refresh-token")
async def refresh_token_():
    data = request.json
    refresh_token = data.get("refresh_token")
    return await refresh_token_controller.refresh_token(refresh_token)
