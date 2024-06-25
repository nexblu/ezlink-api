from utils import (
    UserNotFound,
    Validator,
    EmailNotValid,
    Validator,
    EmailAlreadySend,
    ResetPassword,
    AccountActive,
)
from config import API_URL
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from flask_jwt_extended import JWTManager
from database import UserCRUD, AccountActiveCRUD, ResetPasswordCRUD
from flask_bcrypt import Bcrypt
from flask import jsonify, url_for, request, redirect, render_template
from sqlalchemy.exc import IntegrityError
import smtplib
from email.mime.text import MIMEText
from config import (
    SMTP_PASSWORD,
    SMTP_EMAIL,
    SMTP_SERVER,
    SMTP_PORT,
    API_URL,
    EZLINK_URL,
)
import datetime
from email_validator import validate_email, EmailNotValidError


class AuthController:
    def __init__(self) -> None:
        self.user_database = UserCRUD()
        self.bcrypt = Bcrypt()
        self.jwt = JWTManager()
        self.account_active_database = AccountActiveCRUD()
        self.reset_password_database = ResetPasswordCRUD()

    async def refresh_token(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return (
            jsonify(
                {
                    "success": True,
                    "status_code": 201,
                    "message": "success create new access token",
                    "data": {"token": access_token},
                    "errors": None,
                }
            ),
            201,
        )

    async def email_verify(self, email):
        if not email or email.isspace():
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "email is empety",
                        "data": {"email": email},
                        "errors": {"email": "email is empety"},
                    }
                ),
                400,
            )
        try:
            user = await self.user_database.get("email", email=email)
        except UserNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "user not found",
                        "data": {"email": email},
                        "errors": None,
                    }
                ),
                404,
            )
        else:
            if user.is_active:
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 400,
                            "message": "user is active",
                            "data": {
                                "user_id": user.id,
                                "username": user.username,
                                "email": user.email,
                            },
                            "errors": None,
                        }
                    ),
                    400,
                )
            created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
            expired_at = created_at + (datetime.timedelta(hours=7).total_seconds())
            token = await AccountActive.insert(user.id, email)
            try:
                await self.account_active_database.insert(
                    user.id,
                    token,
                    created_at,
                    expired_at,
                )
            except EmailAlreadySend:
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 400,
                            "message": "user already get link account active",
                            "data": {
                                "user_id": user.id,
                                "username": user.username,
                                "email": user.email,
                            },
                            "errors": None,
                        }
                    ),
                    400,
                )
            else:
                msg = MIMEText(
                    f"""<h1>Hi, Welcome {email}</h1>

    <p>Di Sini Kami Telah Mengirimkan Anda Untuk Verif Account: </p>
    <a href={API_URL}{url_for("api auth.account_active", token=token)}>Click Ini Untuk Verify Email</a>
    """,
                    "html",
                )
                msg["Subject"] = "Verify Email"
                msg["From"] = SMTP_EMAIL
                msg["To"] = email

                try:
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SMTP_EMAIL, SMTP_PASSWORD)
                        server.send_message(msg)
                        server.quit()
                except:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "status_code": 500,
                                "message": "SMPTP error",
                                "data": {
                                    "user_id": user.id,
                                    "username": user.username,
                                    "email": user.email,
                                },
                                "errors": None,
                            }
                        ),
                        500,
                    )
                else:
                    return (
                        jsonify(
                            {
                                "success": True,
                                "status_code": 201,
                                "message": {"email": f"success send link email active"},
                                "data": {
                                    "email": email,
                                    "user_id": user.id,
                                    "username": user.username,
                                    "link": f"{API_URL}{url_for(
                                    "api auth.account_active", token=token
                                )}",
                                },
                                "errors": None,
                            }
                        ),
                        201,
                    )

    async def get_account_active(self, token):
        if valid_token := await AccountActive.get(token):
            try:
                user_token_database = await self.account_active_database.get(
                    "token", user_id=valid_token["user_id"], token=token
                )
            except UserNotFound:
                await self.account_active_database.delete(
                    "user_id", user_id=valid_token["user_id"]
                )
                return render_template("not_found.html")
            else:
                user, account_active = user_token_database
                try:
                    await self.user_database.update(
                        "is_active",
                        is_active=True,
                        email=valid_token["email"],
                    )
                except:
                    await self.account_active_database.delete(
                        "user_id", user_id=account_active.user_id
                    )
                    return render_template("not_found.html")
                else:
                    await self.account_active_database.delete(
                        "user_id", user_id=account_active.user_id
                    )
                    return render_template(
                        "account_active.html",
                        url=EZLINK_URL,
                        username=user.username,
                    )
        return render_template("not_found.html")

    async def get_reset_password(self, token):
        valid_token = await ResetPassword.get(token)
        if request.method == "POST":
            user_change_password = await self.user_database.get(
                "email", email=valid_token["email"]
            )
            data = request.form
            password = data.get("inputPassword")
            confirm_password = data.get("inputConfirmPassword")
            password_error = ""
            confirm_password_error = ""
            if not password.strip():
                password_error = "password is required"
            if not confirm_password.strip():
                confirm_password_error = "confirm password is required"
            if password.strip() != confirm_password.strip():
                password_error = "password do not match"
                confirm_password_error = "password do not match"
            if not password_error and not confirm_password_error:
                try:
                    secure_password = Validator.check_password_strength(password)
                except:
                    return render_template(
                        "reset_password.html",
                        password_error="password not secure",
                        confirm_password_error="password not secure",
                        token=token,
                    )
                else:
                    updated_at = datetime.datetime.now(
                        datetime.timezone.utc
                    ).timestamp()
                    hashed_password = self.bcrypt.generate_password_hash(
                        secure_password
                    ).decode("utf-8")
                    await self.user_database.update(
                        "password",
                        user_id=user_change_password.id,
                        new_password=hashed_password,
                        updated_at=updated_at,
                    )
                    await self.reset_password_database.delete(
                        "user_id", user_id=user_change_password.id
                    )
                    return redirect(EZLINK_URL)
            return render_template(
                "reset_password.html",
                password_error=password_error,
                confirm_password_error=confirm_password_error,
                token=token,
            )
        if valid_token:
            try:
                user_token_database = await self.reset_password_database.get(
                    "token", user_id=valid_token["user_id"], token=token
                )
            except:
                await self.reset_password_database.delete(
                    "email", email=valid_token["email"]
                )
            else:
                return render_template("reset_password.html", token=token)
        return "Invalid token"

    async def reset_password(self, email):
        if not email or email.isspace():
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "email is empety",
                        "data": {"email": email},
                        "errors": {"email": "email is empety"},
                    }
                ),
                400,
            )
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
        except EmailNotValidError as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": f"{email!r} not valid",
                        "data": {"email": email},
                        "errors": {"email": f"email not valid"},
                    }
                ),
                400,
            )
        try:
            user_email = await self.user_database.get("email", email=email)
        except UserNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "user not found",
                        "data": {"email": email},
                        "errors": None,
                    }
                ),
                404,
            )
        token = await ResetPassword.insert(user_email.id, user_email.email)
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        expired_at = created_at + (datetime.timedelta(hours=7).total_seconds())
        try:
            user = await self.reset_password_database.insert(
                user_email.id, token, created_at, expired_at
            )
        except EmailAlreadySend:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "link reset password already send",
                        "data": {"email": email},
                        "errors": None,
                    }
                ),
                400,
            )
        else:
            msg = MIMEText(
                f"""<h1>Hi, Welcome {email}</h1>

    <p>Di Sini Kami Telah Mengirimkan Anda Untuk Merubah Password Anda: </p>
    <a href={API_URL}{url_for("api auth.reset_password", token=token)}>Click Ini Untuk Reset Password</a>
    """,
                "html",
            )
            msg["Subject"] = "Reset Password"
            msg["From"] = SMTP_EMAIL
            msg["To"] = email
            try:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(SMTP_EMAIL, SMTP_PASSWORD)
                    server.send_message(msg)
                    server.quit()
            except:
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 500,
                            "message": "SMTP error",
                            "data": {
                                "user_id": user.id,
                                "username": user.username,
                                "email": user.email,
                            },
                            "errors": None,
                        }
                    ),
                    500,
                )
            else:
                return (
                    jsonify(
                        {
                            "success": True,
                            "status_code": 201,
                            "message": "success send link reset password",
                            "data": {
                                "email": email,
                                "user_id": user.id,
                                "username": user_email.username,
                                "link": f'{API_URL}{url_for(
                                    "api auth.reset_password", token=token
                                )}',
                            },
                            "errors": None,
                        }
                    ),
                    201,
                )

    async def register(self, username, email, password, confirm_password):
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

    async def login(self, email, password):
        if errors := await Validator.validate_login(email, password):
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": "input invalid",
                        "data": {"email": email, "password": password},
                        "errors": errors,
                    }
                ),
                400,
            )
        try:
            user = await self.user_database.get("email", email=email)
        except UserNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "user not found",
                        "data": {"email": email, "password": password},
                        "errors": None,
                    }
                ),
                404,
            )
        else:
            if not user.is_active:
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 400,
                            "message": "user is not active",
                            "data": {
                                "email": email,
                                "username": user.username,
                                "user_id": user.id,
                                "is_active": user.is_active,
                                "created_at": user.created_at,
                                "updated_at": user.updated_at,
                                "banned_at": user.banned_at,
                                "unbanned_at": user.unbanned_at,
                                "profile_image": f'{API_URL}{url_for(
                                    "api user.get_avatar",
                                    user_id=user.id,
                                    profile_name=user.profile_name,
                                )}',
                            },
                            "errors": None,
                        }
                    ),
                    400,
                )
            try:
                if self.bcrypt.check_password_hash(user.password, password):
                    access_token = create_access_token(identity=user)
                    refresh_token = create_refresh_token(identity=user)
                    return (
                        jsonify(
                            {
                                "success": True,
                                "status_code": 200,
                                "message": f"user was found",
                                "data": {
                                    "user_id": user.id,
                                    "username": user.username,
                                    "email": user.email,
                                    "is_active": user.is_active,
                                    "created_at": user.created_at,
                                    "updated_at": user.updated_at,
                                    "banned_at": user.banned_at,
                                    "unbanned_at": user.unbanned_at,
                                    "profile_image": f'{API_URL}{url_for(
                                        "api user.get_avatar",
                                        user_id=user.id,
                                        profile_name=user.profile_name,
                                    )}',
                                    "token": {
                                        "access_token": access_token,
                                        "refresh_token": refresh_token,
                                    },
                                },
                            }
                        ),
                        200,
                    )
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 404,
                            "message": "user not found",
                            "data": {"email": email, "password": password},
                            "errors": None,
                        }
                    ),
                    404,
                )
            except TypeError:
                return (
                    jsonify(
                        {
                            "success": False,
                            "status_code": 404,
                            "message": "user not found",
                            "data": {"email": email, "password": password},
                            "errors": None,
                        }
                    ),
                    404,
                )
