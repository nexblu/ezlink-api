from flask import Blueprint
from controllers import EmailController

email_router = Blueprint("api email", __name__)


@email_router.get("/illustra-line/v1/email-validator/<string:email>")
async def email_validator(email):
    return await EmailController.email_validator(email)
