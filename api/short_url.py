from flask import Blueprint, request
from controllers import ShortURLController
from utils import token_required

short_url_router = Blueprint("api user short url", __name__)
short_url_controller = ShortURLController()


@short_url_router.post("/ez-link/v1/short-url")
@token_required()
async def add_short_url():
    user = request.user
    data = request.json
    url = data.get("url")
    aliases = data.get("aliases")
    return await short_url_controller.add_short_url(user, url, aliases)


@short_url_router.get("/ez-link/v1/short-url")
@token_required()
async def get_short_url():
    user = request.user
    return await short_url_controller.get_short_url(user)


@short_url_router.get("/ez-link/<string:uuid>")
async def redirect_short_url(uuid):
    return await short_url_controller.redirect_short_url(uuid)


@short_url_router.route("/image/<string:uuid>")
async def get_image(uuid):
    return await short_url_controller.get_image_url(uuid)


@short_url_router.route("/download/image/<string:uuid>")
async def download_image(uuid):
    return await short_url_controller.download_image_url(uuid)
