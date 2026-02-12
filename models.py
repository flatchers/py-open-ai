from sqlalchemy import Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)

    storages: Mapped["StorageModel"] = relationship("StorageModel", back_populates="session")


class StorageModel(Base):
    __tablename__ = "storages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    chat_session: Mapped["ChatSessionModel"] = relationship("ChatSessionModel", back_populates="storage")

    chat_session_id: Mapped[int] = mapped_column(ForeignKey(ChatSessionModel.id, ondelete="CASCADE"))
