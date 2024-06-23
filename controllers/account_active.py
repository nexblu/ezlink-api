from database import AccountActiveCRUD, UserCRUD
from flask import jsonify, render_template
from utils import AccountActive, UserNotFound, EmailAlreadySend
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


class AccountActiveController:
    def __init__(self) -> None:
        self.account_active_database = AccountActiveCRUD()
        self.user_database = UserCRUD()

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
    <a href={API_URL}/ez-link/v1/user/email-verify/{token}>Click Ini Untuk Verify Email</a>
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
                                    "link": f"{API_URL}/ez-link/v1/user/email-verify/{token}",
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
