from db.database import Base
from sqlalchemy import (ForeignKey, DateTime)
from sqlalchemy.orm import (Mapped, mapped_column, relationship)
from datetime import (datetime, timedelta)


class Developers(Base):

    __tablename__ = "developers"

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    email:Mapped[str] = mapped_column(unique=True, index=True)
    hash_password:Mapped[str] = mapped_column()
    verified:Mapped[bool] = mapped_column(default=False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    projects:Mapped[list["Projects"]] = relationship("Projects", back_populates="developer")

class Projects(Base):

    __tablename__ = "projects"

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    developer_id:Mapped[int] = mapped_column(ForeignKey("developers.id", ondelete="CASCADE"), index=True)
    project_name:Mapped[str] = mapped_column()
    api:Mapped[str] = mapped_column(index=True, unique=True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    developer:Mapped["Developers"] = relationship("Developers", back_populates="projects")
    users:Mapped[list["End_Users"]] = relationship("End_Users", back_populates="app")


class End_Users(Base):

    __tablename__ = "end_users"

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    project_id:Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    email:Mapped[str] = mapped_column(index=True, unique=True)
    name:Mapped[str] = mapped_column()
    user_end_hashedpass:Mapped[str] = mapped_column()
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    app:Mapped["Projects"] = relationship("Projects", back_populates="users")


class Tokens(Base):

    __tablename__ = "tokens"

    id:Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    developer_id:Mapped[int|None] = mapped_column(ForeignKey("developers.id", ondelete="CASCADE"), nullable=True, index=True)
    end_user_id:Mapped[int|None] = mapped_column(ForeignKey("end_users.id", ondelete="CASCADE"), nullable=True, index=True)
    token_hashed:Mapped[str] = mapped_column(index=True)
    token_type:Mapped[str] = mapped_column()
    expires_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now()+timedelta(minutes=30))
    used_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)



    


