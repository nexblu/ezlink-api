from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    Float,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from database import Base


class WalletDatabase(Base):
    __tablename__ = "wallet"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete=("CASCADE")),
        unique=True,
        nullable=False,
    )
    amount = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(Float, nullable=False)
    updated_at = Column(Float, nullable=False)
    banned_at = Column(Float, nullable=True)
    unbanned_at = Column(Float, nullable=True)

    user = relationship("UserDatabase", back_populates="wallet")

    __table_args__ = (
        CheckConstraint("user_id > 0", name="positive_user_id"),
        CheckConstraint("created_at > 0", name="positive_created_at"),
        CheckConstraint("updated_at > 0", name="positive_updated_at"),
        CheckConstraint(
            "(banned_at > 0) OR (banned_at IS NULL)", name="positive_banned_at_or_null"
        ),
        CheckConstraint(
            "(unbanned_at > 0) OR (unbanned_at IS NULL)",
            name="positive_un_banned_at_or_null",
        ),
    )

    def __init__(self, user_id, created_at, updated_at):
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return f"<Wallet '{self.user_id}'>"
