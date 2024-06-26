from sqlalchemy import (
    Column,
    Integer,
    String,
    LargeBinary,
    Float,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base
import qrcode
import io
import validators
from utils import ShortURLNotAvaible


class ShortURLDatabase(Base):
    __tablename__ = "short_url"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete=("CASCADE")),
        unique=True,
        nullable=False,
    )
    url = Column(String, unique=True, nullable=False)
    aliases = Column(String, unique=True, nullable=True)
    name_file = Column(String, nullable=False)
    qr_code = Column(LargeBinary, nullable=False)
    created_at = Column(Float, nullable=False)
    updated_at = Column(Float, nullable=False)

    user = relationship("UserDatabase", back_populates="short_url")

    __table_args__ = (
        CheckConstraint("user_id > 0", name="positive_user_id"),
        CheckConstraint("length(url) > 0", name="non_empty_url"),
        CheckConstraint("length(aliases) > 0", name="non_empty_aliases"),
        CheckConstraint("created_at > 0", name="positive_created_at"),
        CheckConstraint("updated_at > 0", name="positive_updated_at"),
    )

    def __init__(self, user_id, url, created_at, updated_at):
        self.user_id = user_id
        self.url = url
        self.created_at = created_at
        self.updated_at = updated_at
        self.name_file = f"{created_at}_{user_id}"
        self.qr_code = self.generate_qr_code()

    def __repr__(self):
        return f"<Short URL '{self.user_id}'>"

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        img_pil = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img_pil.save(img_buffer, format="PNG")
        img_byte_data = img_buffer.getvalue()
        return img_byte_data

    def valid_url(self):
        if validators.url(self.url):
            return self.url
        raise ShortURLNotAvaible
