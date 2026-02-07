from typing import List
from sqlalchemy import DateTime, ForeignKey, JSON, func   # func is a special object instance that generates sql based on name-based attributes
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class UserModel(Base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    name: Mapped[str] = mapped_column(nullable = False)
    email: Mapped[str] = mapped_column(nullable = False)
    password_hash: Mapped[str] = mapped_column(nullable = False)

    files: Mapped[List["FileModel"]] = relationship(back_populates = "user")

class FileModel(Base):
    __tablename__ = "files_table"

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["UserModel"] = relationship(back_populates = "files")
    file_name: Mapped[str] = mapped_column(nullable = False)
    file_type: Mapped[str] = mapped_column(nullable = False)
    uploaded_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone = True),
        server_default = func.now(),
        nullable = False
    )
    summary: Mapped[str] = mapped_column(nullable = True)
    
    chunks: Mapped[List["ChunkModel"]] = relationship(back_populates = "file")

class ChunkModel(Base):
    __tablename__ = "chunks_table"

    id: Mapped[int] = mapped_column(primary_key = True, index = True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files_table.id"))
    text: Mapped[str] = mapped_column(nullable = False)
    embedding: Mapped[list[float]] = mapped_column(JSON, nullable = False)

    file: Mapped["FileModel"] = relationship(back_populates = "chunks")