"""
Blog and news management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from api.models import (
    BlogPostCreate, BlogPostUpdate, BlogPostResponse,
    PostCommentCreate, PostCommentResponse,
    PaginationParams, PaginatedResponse, BaseResponse
)
from api.auth import get_current_user, require_roles
from api.database import get_db
from models.models import BlogPost, PostComment, User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse)
async def get_blog_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query("PUBLISHED"),
    db: Session = Depends(get_db)
):
    """
    Get list of blog posts with pagination and filtering
    """
    query = db.query(BlogPost)

    # Apply filters
    if search:
        query = query.filter(
            or_(
                BlogPost.title.ilike(f"%{search}%"),
                BlogPost.content.ilike(f"%{search}%"),
                BlogPost.excerpt.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(BlogPost.category == category)

    if status:
        query = query.filter(BlogPost.status == status)

    # Order by published date (newest first)
    query = query.order_by(desc(BlogPost.published_at))

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * size
    posts_query = query.offset(offset).limit(size).all()

    posts = []
    for post in posts_query:
        posts.append(BlogPostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            content=post.content,
            excerpt=post.excerpt,
            author={
                "id": post.author.id,
                "first_name": post.author.first_name,
                "last_name": post.author.last_name
            },
            category=post.category,
            status=post.status,
            featured_image=post.featured_image,
            tags=post.tags.split(',') if post.tags else [],
            view_count=post.view_count,
            is_featured=post.is_featured,
            allow_comments=post.allow_comments,
            published_at=post.published_at,
            meta_title=post.meta_title,
            meta_description=post.meta_description,
            created_at=post.created_at,
            updated_at=post.updated_at
        ).dict())

    pages = (total + size - 1) // size
    has_next = page < pages
    has_previous = page > 1

    return PaginatedResponse(
        data=posts,
        pagination={
            "page": page,
            "size": size,
            "total": total,
            "pages": pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    )

@router.get("/{slug}", response_model=BlogPostResponse)
async def get_blog_post(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific blog post by slug
    """
    post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    # Increment view count
    post.view_count += 1
    db.add(post)
    db.commit()
    db.refresh(post)

    return BlogPostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        excerpt=post.excerpt,
        author={
            "id": post.author.id,
            "first_name": post.author.first_name,
            "last_name": post.author.last_name
        },
        category=post.category,
        status=post.status,
        featured_image=post.featured_image,
        tags=post.tags.split(',') if post.tags else [],
        view_count=post.view_count,
        is_featured=post.is_featured,
        allow_comments=post.allow_comments,
        published_at=post.published_at,
        meta_title=post.meta_title,
        meta_description=post.meta_description,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@router.post("/", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    post_data: BlogPostCreate,
    current_user: User = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Create a new blog post
    """
    # Check if slug already exists
    if db.query(BlogPost).filter(BlogPost.slug == post_data.slug).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists"
        )

    new_post = BlogPost(
        title=post_data.title,
        slug=post_data.slug,
        content=post_data.content,
        excerpt=post_data.excerpt,
        author_id=current_user.id,
        category=post_data.category,
        status=post_data.status,
        featured_image=post_data.featured_image,
        tags=','.join(post_data.tags) if post_data.tags else None,
        is_featured=post_data.is_featured,
        allow_comments=post_data.allow_comments,
        published_at=post_data.published_at,
        meta_title=post_data.meta_title,
        meta_description=post_data.meta_description
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return BlogPostResponse(
        id=new_post.id,
        title=new_post.title,
        slug=new_post.slug,
        content=new_post.content,
        excerpt=new_post.excerpt,
        author={
            "id": new_post.author.id,
            "first_name": new_post.author.first_name,
            "last_name": new_post.author.last_name
        },
        category=new_post.category,
        status=new_post.status,
        featured_image=new_post.featured_image,
        tags=new_post.tags.split(',') if new_post.tags else [],
        view_count=new_post.view_count,
        is_featured=new_post.is_featured,
        allow_comments=new_post.allow_comments,
        published_at=new_post.published_at,
        meta_title=new_post.meta_title,
        meta_description=new_post.meta_description,
        created_at=new_post.created_at,
        updated_at=new_post.updated_at
    )

@router.put("/{post_id}", response_model=BlogPostResponse)
async def update_blog_post(
    post_id: int,
    post_data: BlogPostUpdate,
    current_user: User = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Update an existing blog post
    """
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    # Check if user is author or admin
    if post.author_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this post"
        )

    # Check if new slug already exists (if changed)
    if post_data.slug and post_data.slug != post.slug:
        if db.query(BlogPost).filter(BlogPost.slug == post_data.slug).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug already exists"
            )

    # Update fields
    for field, value in post_data.dict(exclude_unset=True).items():
        if field == "tags" and value:
            setattr(post, field, ','.join(value))
        else:
            setattr(post, field, value)

    db.add(post)
    db.commit()
    db.refresh(post)

    return BlogPostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        content=post.content,
        excerpt=post.excerpt,
        author={
            "id": post.author.id,
            "first_name": post.author.first_name,
            "last_name": post.author.last_name
        },
        category=post.category,
        status=post.status,
        featured_image=post.featured_image,
        tags=post.tags.split(',') if post.tags else [],
        view_count=post.view_count,
        is_featured=post.is_featured,
        allow_comments=post.allow_comments,
        published_at=post.published_at,
        meta_title=post.meta_title,
        meta_description=post.meta_description,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@router.delete("/{post_id}", response_model=BaseResponse)
async def delete_blog_post(
    post_id: int,
    current_user: User = Depends(require_roles(["ADMIN", "TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Delete a blog post
    """
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    # Check if user is author or admin
    if post.author_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )

    db.delete(post)
    db.commit()

    return BaseResponse(message="Blog post deleted successfully")

@router.get("/{post_id}/comments", response_model=List[PostCommentResponse])
async def get_post_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comments for a blog post
    """
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    comments = db.query(PostComment).filter(PostComment.post_id == post_id).order_by(desc(PostComment.created_at)).all()

    return [
        PostCommentResponse(
            id=comment.id,
            post_id=comment.post_id,
            author_name=comment.author_name,
            author_email=comment.author_email,
            content=comment.content,
            is_approved=comment.is_approved,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        ) for comment in comments
    ]

@router.post("/{post_id}/comments", response_model=PostCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_post_comment(
    post_id: int,
    comment_data: PostCommentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a comment on a blog post
    """
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    if not post.allow_comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are not allowed on this post"
        )

    new_comment = PostComment(
        post_id=post_id,
        author_name=comment_data.author_name,
        author_email=comment_data.author_email,
        content=comment_data.content,
        is_approved=False  # Comments need approval by default
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return PostCommentResponse(
        id=new_comment.id,
        post_id=new_comment.post_id,
        author_name=new_comment.author_name,
        author_email=new_comment.author_email,
        content=new_comment.content,
        is_approved=new_comment.is_approved,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at
    )
