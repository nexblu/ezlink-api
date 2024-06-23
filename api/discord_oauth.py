from flask import Blueprint
from controllers import DiscordOauthController

discord_oauth_router = Blueprint("api_discord_oauth_login", __name__)
discord_oauth_controller = DiscordOauthController()


@discord_oauth_router.route("/oauth/callback")
async def discord_callback():
    return await discord_oauth_controller.oauth_callback()


@discord_oauth_router.route("/discord/oauth")
async def discord_oauth():
    return await discord_oauth_controller.discord_oauth()
