from database import ShortURLCRUD
from flask import jsonify, redirect, send_file
import shortuuid
from utils import ShortURLNotFound, ShortURLNotAvaible
import datetime
from config import API_URL
from io import BytesIO


class ShortURLController:
    def __init__(self) -> None:
        self.short_url_database = ShortURLCRUD()

    async def download_image_url(self, uuid):
        try:
            image = await self.short_url_database.get("uuid", uuid=uuid)
        except ShortURLNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "url not found",
                        "data": {
                            "url": f"{API_URL}/image/{uuid}",
                        },
                        "errors": None,
                    }
                ),
                404,
            )
        else:
            return send_file(
                BytesIO(image.qr_code),
                mimetype="image/jpeg",
                as_attachment=True,
                download_name="image_uuid.jpg",
            )

    async def get_image_url(self, uuid):
        try:
            image = await self.short_url_database.get("uuid", uuid=uuid)
        except ShortURLNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "url not found",
                        "data": {
                            "url": f"{API_URL}/image/{uuid}",
                        },
                        "errors": None,
                    }
                ),
                404,
            )
        else:
            return send_file(
                BytesIO(image.qr_code),
                mimetype="image/jpeg",
                download_name="image_uuid.jpg",
            )

    async def get_short_url(self, user):
        try:
            result = await self.short_url_database.get("user", user_id=user.id)
        except ShortURLNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "shorturl not found",
                        "data": {
                            "user_id": user.id,
                            "username": user.username,
                            "email": user.email,
                        },
                        "errors": None,
                    }
                ),
                404,
            )
        else:
            return (
                jsonify(
                    {
                        "success": True,
                        "status_code": 200,
                        "message": "shorturl was found",
                        "data": [
                            {
                                "short_url": f"{API_URL}/ez-link/{data.uuid if data.aliases == None else data.aliases}",
                                "user_id": user.id,
                                "username": user.username,
                                "email": user.email,
                                "created_at": data.created_at,
                                "original_url": data.url,
                                "image_url": f"{API_URL}/image/{data.uuid}",
                                "download_image": f"{API_URL}/download/image/{data.uuid}",
                            }
                            for data in result
                        ],
                        "errors": None,
                    }
                ),
                200,
            )

    async def redirect_short_url(self, uuid):
        try:
            result = await self.short_url_database.get("uuid", uuid=uuid)
        except ShortURLNotFound:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 404,
                        "message": "url not found",
                        "data": None,
                    }
                ),
                404,
            )
        else:
            return redirect(result.url)

    async def add_short_url(self, user, url, aliases):
        if not url or url.isspace():
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": {"url": "url is empety"},
                        "data": {
                            "url": url,
                            "user_id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "aliases": aliases,
                        },
                    }
                ),
                400,
            )
        created_at = datetime.datetime.now(datetime.timezone.utc).timestamp()
        try:
            result = await self.short_url_database.insert(
                user.id,
                url,
                shortuuid.uuid()[:8],
                created_at,
                aliases=aliases,
            )
        except ShortURLNotAvaible:
            return (
                jsonify(
                    {
                        "success": False,
                        "status_code": 400,
                        "message": {"url": f"{url!r} not avaible"},
                        "data": {
                            "user_id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "url": url,
                            "aliases": aliases,
                        },
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
                        "message": f"successfully add short url {url!r}",
                        "data": {
                            "short_url": f"{API_URL}/ez-link/{result.uuid if result.aliases == None else result.aliases}",
                            "user_id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "url": result.url,
                            "created_at": result.created_at,
                            "aliases": aliases,
                            "image_url": f"{API_URL}/image/{result.uuid}",
                            "download_image": f"{API_URL}/download/image/{result.uuid}",
                        },
                    }
                ),
                201,
            )
