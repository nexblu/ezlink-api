from flask import jsonify
from flask_bcrypt import Bcrypt
from database import UserCRUD
from sqlalchemy.exc import IntegrityError
from utils import EmailNotValid, Validator


class RegisterController:
    def __init__(self) -> None:
        self.user_database = UserCRUD()
        self.bcrypt = Bcrypt()

    async def add_user(self, username, email, password, confirm_password):
        if errors := await Validator.validate_register(
            username, email, password, confirm_password
        ):
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "invalid input",
                        "data": {
                            "username": username,
                            "email": email,
                            "password": password,
                            "confirm_password": confirm_password,
                        },
                        "errors": errors,
                    }
                ),
                400,
            )
        if not (password_secure := Validator.check_password_strength(password)):
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "password not secure",
                        "data": {
                            "username": username,
                            "email": email,
                            "password": password,
                            "confirm_password": confirm_password,
                        },
                        "errors": {
                            "password": "password not secure",
                            "confirm_password": "password not secure",
                        },
                    }
                ),
                400,
            )
        try:
            hashed_password = self.bcrypt.generate_password_hash(password).decode(
                "utf-8"
            )
            result = await self.user_database.insert(
                username=username,
                email=email,
                password=hashed_password,
            )
        except IntegrityError:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "failed register",
                        "data": {
                            "username": username,
                            "email": email,
                            "password": password,
                            "confirm_password": confirm_password,
                        },
                        "errors": None,
                    }
                ),
                400,
            )
        except EmailNotValid:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "email not valid",
                        "data": {
                            "username": username,
                            "email": email,
                            "password": password,
                            "confirm_password": confirm_password,
                        },
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
                        "status_code": 201,
                        "message": "successfully registered",
                        "data": {
                            "user_id": result.id,
                            "username": username,
                            "email": email,
                            "password": password,
                            "confirm_password": confirm_password,
                        },
                        "errors": None,
                    }
                ),
                201,
            )
