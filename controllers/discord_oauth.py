from flask import request, redirect
from zenora import APIClient
from config import (
    DISCORD_CLIENT_SECRET,
    DISCORD_TOKEN,
    DISCORD_CALLBACK_URL,
    EZLINK_URL,
    DISCORD_OAUTH_URL,
)


class DiscordOauthController:
    def __init__(self) -> None:
        self.client = APIClient(
            DISCORD_TOKEN,
            client_secret=DISCORD_CLIENT_SECRET,
        )

    async def oauth_callback(self):
        code = request.args["code"]
        access_token = self.client.oauth.get_access_token(
            code,
            DISCORD_CALLBACK_URL,
        ).access_token
        bearer_client = APIClient(access_token, bearer=True)
        user = bearer_client.users.get_current_user()
        print(user)
        return redirect(EZLINK_URL)

    async def discord_oauth(self):
        return redirect(DISCORD_OAUTH_URL)
