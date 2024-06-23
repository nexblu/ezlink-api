from flask import Blueprint, request
from controllers import AccountActiveController

account_active_router = Blueprint("api account active", __name__)
account_active_service = AccountActiveController()


@account_active_router.get("/ez-link/v1/user/email-verify/<string:token>")
async def account_active(token):
    return await account_active_service.get_account_active(token)


@account_active_router.post("/ez-link/v1/user/email-verify")
async def account_active_email():
    data = request.json
    email = data.get("email")
    return await account_active_service.email_verify(email)
