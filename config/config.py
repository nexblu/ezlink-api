from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.environ.get("MONGODB_URL")
POSTGRESQL_URL = os.environ.get("POSTGRESQL_URL")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
ACCOUNT_ACTIVE_KEY = os.environ.get("ACCOUNT_ACTIVE_KEY")
RESET_PASSWORD_KEY = os.environ.get("RESET_PASSWORD_KEY")
ACCOUNT_ACTIVE_SALT = os.environ.get("ACCOUNT_ACTIVE_SALT")
RESET_PASSWORD_SALT = os.environ.get("RESET_PASSWORD_SALT")
SECRET_KEY = os.environ.get("SECRET_KEY")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
CLIENT_SCOPE = os.environ.get("CLIENT_SCOPE")
SERVER_METADATA_URL = os.environ.get("SERVER_METADATA_URL")
NAME_GOOGLE_OAUTH = os.environ.get("NAME_GOOGLE_OAUTH")
DISCORD_CALLBACK_URL = os.environ.get("DISCORD_CALLBACK_URL")
DISCORD_OAUTH_URL = os.environ.get("DISCORD_OAUTH_URL")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
API_URL = os.environ.get("API_URL")
EZLINK_URL = os.environ.get("EZLINK_URL")
