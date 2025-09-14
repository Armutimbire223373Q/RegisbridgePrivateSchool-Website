"""
Public content models (news, events, etc.)
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class NewsPost(BaseModel):
    """News post model"""
    __tablename__ = "news_posts"
    
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, default=True)
    published_at = Column(DateTime, nullable=True)
    featured_image = Column(String(500), nullable=True)
    excerpt = Column(Text, nullable=True)
    
    # Relationships
    author = relationship("User")
    
    def __str__(self):
        return self.title

