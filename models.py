from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Storage(Base):
    __tablename__ = "storages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)

