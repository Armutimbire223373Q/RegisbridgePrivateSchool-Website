"""
Messaging and communication models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class MessageType(str, enum.Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    DOCUMENT = "DOCUMENT"
    ANNOUNCEMENT = "ANNOUNCEMENT"

class MessagePriority(str, enum.Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"

class Thread(BaseModel):
    """Message thread model"""
    __tablename__ = "threads"

    title = Column(String(200), nullable=False)
    thread_type = Column(String(50), nullable=False)  # student_teacher, parent_teacher, admin_announcement, etc.
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime, nullable=True)

    # Relationships
    messages = relationship("Message", back_populates="thread")
    participants = relationship("ThreadParticipant", back_populates="thread")

    def __str__(self):
        return self.title

class Message(BaseModel):
    """Message model"""
    __tablename__ = "messages"

    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    priority = Column(Enum(MessagePriority), default=MessagePriority.NORMAL)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # File attachments
    attachment_path = Column(String(500), nullable=True)
    attachment_name = Column(String(200), nullable=True)
    attachment_size = Column(Integer, nullable=True)

    # Relationships
    thread = relationship("Thread", back_populates="messages")
    sender = relationship("User")
    parent_message = relationship("Message", remote_side="Message.id")
    replies = relationship("Message", back_populates="parent_message")

    def __str__(self):
        return f"Message from {self.sender.username} in {self.thread.title}"

class ThreadParticipant(BaseModel):
    """Thread participant model"""
    __tablename__ = "thread_participants"

    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    last_read_at = Column(DateTime, nullable=True)

    # Relationships
    thread = relationship("Thread", back_populates="participants")
    user = relationship("User")

    def __str__(self):
        return f"{self.user.username} in {self.thread.title}"

class Notification(BaseModel):
    """Notification model"""
    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # message, grade, attendance, payment, etc.
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    action_url = Column(String(500), nullable=True)
    priority = Column(Enum(MessagePriority), default=MessagePriority.NORMAL)

    # Relationships
    user = relationship("User")

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

class Announcement(BaseModel):
    """School announcement model"""
    __tablename__ = "announcements"

    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_audience = Column(String(100), nullable=False)  # all, students, parents, teachers, staff
    priority = Column(Enum(MessagePriority), default=MessagePriority.NORMAL)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    author = relationship("User")

    def __str__(self):
        return self.title