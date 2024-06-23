from .token import Token
from itsdangerous.url_safe import URLSafeSerializer
from config import RESET_PASSWORD_KEY, RESET_PASSWORD_SALT


class ResetPassword(Token):
    @staticmethod
    async def insert(user_id, email):
        s = URLSafeSerializer(RESET_PASSWORD_KEY, salt=RESET_PASSWORD_SALT)
        token = s.dumps({"user_id": user_id, "email": email})
        return token

    @staticmethod
    async def get(token):
        s = URLSafeSerializer(RESET_PASSWORD_KEY, salt=RESET_PASSWORD_SALT)
        try:
            s.loads(token)["user_id"]
            s.loads(token)["email"]
        except:
            return None
        else:
            return s.loads(token)
