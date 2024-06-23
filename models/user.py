from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    CheckConstraint,
    LargeBinary,
)
from database import Base
from sqlalchemy.orm import relationship
from PIL import Image
import io
import datetime
from utils import Validator


class UserDatabase(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(Float, nullable=False)
    updated_at = Column(Float, nullable=False)
    banned_at = Column(Float, nullable=True)
    unbanned_at = Column(Float, nullable=True)
    profile_name = Column(String, unique=True, nullable=False)
    profile_image = Column(LargeBinary, nullable=False)

    __table_args__ = (
        CheckConstraint("length(username) > 0", name="non_empty_username"),
        CheckConstraint("length(email) > 0", name="non_empty_email"),
        CheckConstraint("length(password) > 0", name="non_empty_password"),
        CheckConstraint("updated_at > 0", name="positive_updated_at"),
        CheckConstraint("created_at > 0", name="positive_created_at"),
        CheckConstraint(
            "(banned_at > 0) OR (banned_at IS NULL)", name="positive_banned_at_or_null"
        ),
        CheckConstraint(
            "(unbanned_at > 0) OR (unbanned_at IS NULL)",
            name="positive_un_banned_at_or_null",
        ),
    )

    account_active = relationship(
        "AccountActiveDatabase", back_populates="user", uselist=False
    )
    wallet = relationship("WalletDatabase", back_populates="user", uselist=False)
    reset_password = relationship(
        "ResetPasswordDatabase", back_populates="user", uselist=False
    )
    short_url = relationship("ShortURLDatabase", back_populates="user", uselist=False)

    def __init__(self, username, email, password, created_at, updated_at):
        self.username = username
        self.email = Validator.validate_email(email)
        self.password = Validator.check_password_strength(password)
        self.created_at = created_at
        self.updated_at = updated_at
        self.profile_name = f"{datetime.datetime.now(datetime.timezone.utc).timestamp()}_{self.username}"
        self.profile_image = self.image_to_large_binary()

    def __repr__(self):
        return f"<User {self.email!r}>"

    @staticmethod
    def image_to_large_binary():
        image = Image.open("./static/image/profile.jpg")
        with io.BytesIO() as output:
            image.save(output, format="JPEG")
            binary_data = output.getvalue()

        return binary_data
