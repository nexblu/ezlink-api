from authlib.integrations.flask_client import OAuth
from config import (
    CLIENT_ID,
    CLIENT_SCOPE,
    CLIENT_SECRET,
    NAME_GOOGLE_OAUTH,
    SERVER_METADATA_URL,
    EZLINK_URL,
)
from flask import url_for, session, redirect


class GoogleOauthController:
    def __init__(self) -> None:
        self.google_oauth = OAuth()
        self.google = self.google_oauth.register(
            name=NAME_GOOGLE_OAUTH,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            client_kwargs={"scope": CLIENT_SCOPE},
            server_metadata_url=SERVER_METADATA_URL,
        )

    async def google_login(self):
        redirect_url = url_for(
            "api_google_oauth_login.authorize_google", _external=True
        )
        return self.google.authorize_redirect(redirect_url)

    async def authorize_google(self):
        token = self.google.authorize_access_token()
        user_info_endpoint = self.google.server_metadata["userinfo_endpoint"]
        resp = self.google.get(user_info_endpoint)
        user_info = resp.json()
        email = user_info["email"]
        session["user"] = email
        session["oauth_token"] = token
        print(user_info)
        return redirect(EZLINK_URL)
