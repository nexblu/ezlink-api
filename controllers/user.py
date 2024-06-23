from database import UserCRUD
from flask import send_file, jsonify
from io import BytesIO
from utils import UserNotFound


class UserController:
    def __init__(self) -> None:
        self.user_database = UserCRUD()

    async def get_avatar(self, user_id, profile_name):
        try:
            user = await self.user_database.get(
                "avatar", user_id=user_id, profile_name=profile_name
            )
        except UserNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "avatar not found",
                        "data": {"user_id": user_id, "profile_name": profile_name},
                        "errors": None,
                    }
                ),
                404,
            )
        else:
            return send_file(
                BytesIO(user.profile_image),
                mimetype="image/jpeg",
                download_name=f"{profile_name}.jpg",
            )
