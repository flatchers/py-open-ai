from decimal import Decimal

from sqlalchemy import Text, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(20, 12),
        default=Decimal("0"),
        nullable=False
    )

    storages: Mapped[list["StorageModel"]] = relationship("StorageModel", back_populates="chat_session")


class StorageModel(Base):
    __tablename__ = "storages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    chat_session: Mapped["ChatSessionModel"] = relationship("ChatSessionModel", back_populates="storages")

    chat_session_id: Mapped[int] = mapped_column(ForeignKey(ChatSessionModel.id, ondelete="CASCADE"), nullable=False)
