from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import NewsPost


def home(request):
    """Homepage view"""
    try:
        news_posts = NewsPost.objects.filter(is_published=True).order_by(
            "-published_date"
        )[:6]
    except:
        news_posts = []

    return render(request, "public/home.html", {"news_posts": news_posts})


def admissions(request):
    """Admissions page view"""
    return render(request, "public/admissions.html")


def about(request):
    """About page view"""
    return render(request, "public/about.html")


def contact(request):
    """Contact page view"""
    if request.method == "POST":
        # Handle contact form submission
        messages.success(
            request, "Thank you for your message. We will get back to you soon!"
        )
        return redirect("public:contact")

    return render(request, "public/contact.html")


def academics(request):
    """Academics page view"""
    return render(request, "public/academics.html")


def student_life(request):
    """Student Life page view"""
    return render(request, "public/student-life.html")


def news_list(request):
    """News list page view"""
    try:
        news_posts = NewsPost.objects.filter(is_published=True).order_by(
            "-published_date"
        )
    except:
        news_posts = []

    return render(request, "public/news_list.html", {"news_posts": news_posts})


def news_detail(request, slug):
    """Individual news post view"""
    try:
        news_post = get_object_or_404(NewsPost, slug=slug, is_published=True)
        # Get related posts (same category, excluding current post)
        related_posts = NewsPost.objects.filter(
            category=news_post.category, is_published=True
        ).exclude(id=news_post.id)[:3]
    except:
        news_post = None
        related_posts = []

    if not news_post:
        messages.error(request, "News post not found.")
        return redirect("public:news_list")

    return render(
        request,
        "public/news_detail.html",
        {"post": news_post, "related_posts": related_posts},
    )


def inventory(request):
    """Inventory management page view"""
    return render(request, "public/inventory.html")


def boarding(request):
    """Boarding portal page view"""
    return render(request, "public/boarding.html")


@login_required
def student_portal_entry(request):
    """Login-protected entry that sends users to the appropriate student area.

    - STUDENT: go to role dashboard
    - Others: reuse dashboard redirect logic
    """
    if getattr(request.user, "role", None) == "STUDENT":
        return redirect("dashboard:student_dashboard")
    return redirect("dashboard:main")
