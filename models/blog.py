"""
Blog and news models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class PostStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

class PostCategory(str, enum.Enum):
    NEWS = "NEWS"
    EVENTS = "EVENTS"
    ANNOUNCEMENTS = "ANNOUNCEMENTS"
    ACADEMIC = "ACADEMIC"
    SPORTS = "SPORTS"
    GENERAL = "GENERAL"

class BlogPost(BaseModel):
    """Blog post model"""
    __tablename__ = "blog_posts"

    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(Enum(PostCategory), nullable=False)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    featured_image = Column(String(500), nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    view_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    allow_comments = Column(Boolean, default=True)
    published_at = Column(DateTime, nullable=True)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)

    # Relationships
    author = relationship("User")
    comments = relationship("PostComment", back_populates="post")

    def __str__(self):
        return self.title

class PostComment(BaseModel):
    """Blog post comment model"""
    __tablename__ = "post_comments"

    post_id = Column(Integer, ForeignKey("blog_posts.id"), nullable=False)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    parent_comment_id = Column(Integer, ForeignKey("post_comments.id"), nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    post = relationship("BlogPost", back_populates="comments")
    approved_by = relationship("User")
    parent_comment = relationship("PostComment", remote_side="PostComment.id")
    replies = relationship("PostComment", back_populates="parent_comment")

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"

class Event(BaseModel):
    """School event model"""
    __tablename__ = "events"

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    location = Column(String(200), nullable=True)
    event_type = Column(String(50), nullable=False)  # academic, sports, cultural, meeting, etc.
    is_public = Column(Boolean, default=True)
    max_attendees = Column(Integer, nullable=True)
    registration_required = Column(Boolean, default=False)
    registration_deadline = Column(DateTime, nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_email = Column(String(200), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    created_by = relationship("User")
    registrations = relationship("EventRegistration", back_populates="event")

    def __str__(self):
        return self.title

class EventRegistration(BaseModel):
    """Event registration model"""
    __tablename__ = "event_registrations"

    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    registrant_name = Column(String(100), nullable=False)
    registrant_email = Column(String(200), nullable=False)
    registrant_phone = Column(String(20), nullable=True)
    registration_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="PENDING")  # PENDING, CONFIRMED, CANCELLED
    notes = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # If registered by logged-in user

    # Relationships
    event = relationship("Event", back_populates="registrations")
    user = relationship("User")

    def __str__(self):
        return f"{self.registrant_name} - {self.event.title}"

class Page(BaseModel):
    """Static page model"""
    __tablename__ = "pages"

    title = Column(String(200), nullable=False)
    slug = Column(String(250), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    is_published = Column(Boolean, default=False)
    is_homepage = Column(Boolean, default=False)
    template = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey("pages.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    parent = relationship("Page", remote_side="Page.id")
    children = relationship("Page", back_populates="parent")
    created_by = relationship("User")

    def __str__(self):
        return self.title

class MediaFile(BaseModel):
    """Media file model"""
    __tablename__ = "media_files"

    filename = Column(String(200), nullable=False)
    original_filename = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_type = Column(String(50), nullable=False)  # image, document, video, audio
    alt_text = Column(String(200), nullable=True)
    caption = Column(Text, nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)

    # Relationships
    uploaded_by = relationship("User")

    def __str__(self):
        return self.original_filename
