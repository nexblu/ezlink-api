from .token import Token
from itsdangerous.url_safe import URLSafeSerializer
from config import ACCOUNT_ACTIVE_KEY, ACCOUNT_ACTIVE_SALT


class AccountActive(Token):
    @staticmethod
    async def insert(user_id, email):
        s = URLSafeSerializer(ACCOUNT_ACTIVE_KEY, salt=ACCOUNT_ACTIVE_SALT)
        token = s.dumps({"user_id": user_id, "email": email})
        return token

    @staticmethod
    async def get(token):
        s = URLSafeSerializer(ACCOUNT_ACTIVE_KEY, salt=ACCOUNT_ACTIVE_SALT)
        try:
            s.loads(token)["user_id"]
            s.loads(token)["email"]
        except:
            return None
        else:
            return s.loads(token)
