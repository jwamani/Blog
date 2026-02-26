from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.functions import func
from datetime import datetime

if __package__ is None or __package__ == '':
    from database import Base
else:
    from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fullname = Column(String(50), index=True)
    email = Column(String(50), index=True, unique=True)
    username = Column(String(50), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String)
    phone_number = Column(String(15), unique=True, index=True, nullable=True)

    posts = relationship('Post', backref='owner', lazy='selectin')  # backref, back_populates, lazy
    comments = relationship('Comment', backref='commenter')
    images = relationship('Image', backref='uploader', lazy='selectin')


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(50), index=True)
    content = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))

    comments = relationship('Comment', backref='for_post', lazy='selectin')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(String(1000))
    user_id = Column(ForeignKey('users.id'))
    post_id = Column(ForeignKey('posts.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_user_post', 'user_id', 'post_id', unique=True),
    )

class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column(Integer)
    uploaded_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))