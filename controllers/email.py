from flask import jsonify
from email_validator import validate_email, EmailNotValidError


class EmailController:
    @staticmethod
    async def email_validator(email):
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
        except EmailNotValidError as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "email not valid",
                        "data": {"email": email},
                        "errors": {"email": "email not valid"},
                    }
                ),
                400,
            )
        else:
            return (
                jsonify(
                    {
                        "success": True,
                        "status_code": 200,
                        "message": "email is valid",
                        "data": {"email": email},
                        "errors": None,
                    }
                ),
                200,
            )
