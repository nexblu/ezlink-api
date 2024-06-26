import re
from .custom_exception import EmailNotValid
from email_validator import validate_email, EmailNotValidError


class Validator:
    @staticmethod
    async def validate_register(username, email, password, confirm_password):
        errors = {}
        if not username or username.isspace():
            errors["username"] = "username is empty"
        if not email or email.isspace():
            errors["email"] = "email is empty"
        if not password or password.isspace():
            errors["password"] = "password is empty"
        if not confirm_password or confirm_password.isspace():
            errors["confirm_password"] = "confirm password is empty"
        if password != confirm_password:
            errors["password"] = "password are not the same"
            errors["confirm_password"] = "password are not the same"
        return errors

    @staticmethod
    async def validate_task(task, tags):
        errors = {}
        if not isinstance(tags, list):
            errors["tags"] = "tags must be array"
        if not task or task.isspace():
            errors["task"] = "task is empty"
        if not tags or len(tags) == 0:
            errors["password"] = "password is empty"
        return errors

    @staticmethod
    async def validate_login(email, password):
        errors = {}
        if (not email or email.isspace()) and (not password or password.isspace()):
            errors["email"] = "email is empty"
            errors["password"] = "password is empty"
        if not email or email.isspace():
            errors["email"] = "email is empty"
        if not password or password.isspace():
            errors["password"] = "password is empty"
        return errors

    @staticmethod
    def check_password_strength(password):
        if len(password) < 8:
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[!@#$%^&*()-+=]", password):
            return False
        return password

    @staticmethod
    def validate_email(email):
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
        except EmailNotValidError as e:
            raise EmailNotValid
        return email
