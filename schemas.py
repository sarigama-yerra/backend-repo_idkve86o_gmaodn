"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
- ContactMessage -> "contactmessage" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password_hash: str = Field(..., description="Salted password hash in 'salt$hash' format")
    is_active: bool = Field(True, description="Whether user is active")

class BlogPost(BaseModel):
    """
    Blog posts collection schema
    Collection name: "blogpost"
    """
    title: str = Field(..., description="Post title")
    slug: str = Field(..., description="URL-friendly slug")
    excerpt: Optional[str] = Field(None, description="Short summary")
    content: str = Field(..., description="Full content (markdown supported)")
    author: str = Field(..., description="Author name")
    published: bool = Field(True, description="Whether post is published")

class ContactMessage(BaseModel):
    """
    Contact messages collection schema
    Collection name: "contactmessage"
    """
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    topic: Optional[str] = Field(None, description="Topic or subject")
    message: str = Field(..., description="Message body")

# Optional example schema kept for reference
class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
