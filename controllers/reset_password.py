from flask import render_template, request, jsonify, redirect, url_for
from utils import ResetPassword
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
from database import UserCRUD, ResetPasswordCRUD
from flask_bcrypt import Bcrypt
from utils import UserNotFound, EmailAlreadySend, Validator
import datetime
from email_validator import validate_email, EmailNotValidError


class ResetPasswordController:
    def __init__(self) -> None:
        self.user_database = UserCRUD()
        self.token_database = ResetPasswordCRUD()
        self.bcrypt = Bcrypt()

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
                        confirm_password_error="password not secure",token=token
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
                    await self.token_database.delete(
                        "user_id", user_id=user_change_password.id
                    )
                    return redirect(EZLINK_URL)
            return render_template(
                "reset_password.html",
                password_error=password_error,
                confirm_password_error=confirm_password_error,token=token
            )
        if valid_token:
            try:
                user_token_database = await self.token_database.get(
                    "token", user_id=valid_token["user_id"], token=token
                )
            except:
                await self.token_database.delete("email", email=valid_token["email"])
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
            user = await self.token_database.insert(
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
    <a href={API_URL}/ez-link/v1/user/reset/reset-password/{token}>Click Ini Untuk Reset Password</a>
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
                                    "route reset password.reset_password", token=token
                                )}',
                            },
                            "errors": None,
                        }
                    ),
                    201,
                )
