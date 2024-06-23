from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base


class AccountActiveDatabase(Base):
    __tablename__ = "account_active"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete=("CASCADE")),
        unique=True,
        nullable=False,
    )
    token = Column(String, unique=True, nullable=False)
    created_at = Column(Float, nullable=False)
    updated_at = Column(Float, nullable=False)
    expired_at = Column(Float, nullable=False)

    user = relationship("UserDatabase", back_populates="account_active")

    __table_args__ = (
        CheckConstraint("user_id > 0", name="positive_user_id"),
        CheckConstraint("length(token) > 0", name="non_empty_token"),
        CheckConstraint("created_at > 0", name="positive_created_at"),
        CheckConstraint("updated_at > 0", name="positive_updated_at"),
        CheckConstraint("expired_at > 0", name="positive_expired_at"),
    )

    def __init__(self, user_id, token, created_at, updated_at, expired_at):
        self.user_id = user_id
        self.token = token
        self.created_at = created_at
        self.updated_at = updated_at
        self.expired_at = expired_at

    def __repr__(self):
        return f"<Account Active '{self.user_id}'>"
