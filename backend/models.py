from typing import List
from sqlalchemy import DateTime, ForeignKey, func   # func is a special object instance that generates sql based on name-based attributes
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from pwdlib import PasswordHash

pwd_password_hash = PasswordHash.recommended()

class User(Base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name: Mapped[str] = mapped_column(nullable = False)
    password_hash: Mapped[str] = mapped_column(nullable = False)
    files: Mapped[List["Files"]] = relationship(back_populates = "user")

    def get_password_hash(self, password):
        self.password_hash = pwd_password_hash.hash(password)

    def verify_password(password, password_hash):
        return pwd_password_hash.verify(password, password_hash)


class Files(Base):
    __tablenme__ = ""

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["User"] = relationship(back_populates = "files")
    file_name: Mapped[str] = mapped_column(nullable = False)
    file_type: Mapped[str] = mapped_column(nullable = False)
    uploaded_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False
    )

    summary: Mapped[str] = mapped_column(nullable = True)
    