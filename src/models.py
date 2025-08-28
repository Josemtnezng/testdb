from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, Text, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

# Tabla intermedia para la relación Muchos a Muchos entre User y Unlockable
user_unlocks = db.Table('user_unlocks',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('unlockable_id', db.Integer, db.ForeignKey('unlockable.id'), primary_key=True)
)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # --- Relaciones ---
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    playlist_videos = relationship("PlaylistVideo", back_populates="user", cascade="all, delete-orphan")
    favorite_themes = relationship("FavoriteTheme", back_populates="user", cascade="all, delete-orphan")
    unlocked_items = relationship("Unlockable", secondary=user_unlocks, back_populates="users")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

class UserProfile(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    active_theme_name: Mapped[str] = mapped_column(String(50), default='Paz')
    points: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_seconds: Mapped[int] = mapped_column(BigInteger, default=0)
    
    user = relationship("User", back_populates="profile")

class PlaylistVideo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    youtube_video_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(255))
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user = relationship("User", back_populates="playlist_videos")

class FavoriteTheme(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    theme_name: Mapped[str] = mapped_column(String(100), nullable=False)
    primary_color: Mapped[str] = mapped_column(String(7))
    accent_color: Mapped[str] = mapped_column(String(7))

    user = relationship("User", back_populates="favorite_themes")

class Unlockable(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    item_type: Mapped[str] = mapped_column(String(50))
    points_cost: Mapped[int] = mapped_column(Integer, nullable=False)

    users = relationship("User", secondary=user_unlocks, back_populates="unlocked_items")