from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView
from django.core.cache import cache
import logging

from blog.models import Post
from .models import (
    AboutPage, AcademicsPage, CurriculumPage,
    StudentLifePage, ContactPage, FAQ, Page
)
from .forms import ContactForm

logger = logging.getLogger(__name__)

# Error handler views
def bad_request(request, exception=None):
    """400 error handler."""
    logger.warning(f"Bad request: {request.path}")
    return render(request, 'main/400.html', status=400)

def permission_denied(request, exception=None):
    """403 error handler."""
    logger.warning(f"Permission denied: {request.path}")
    return render(request, 'main/403.html', status=403)

def page_not_found(request, exception=None):
    """404 error handler."""
    logger.warning(f"Page not found: {request.path}")
    return render(request, 'main/404.html', status=404)

def server_error(request):
    """500 error handler."""
    logger.error(f"Server error: {request.path}")
    return render(request, 'main/500.html', status=500)

def handle_error(request, error_message, redirect_url=None):
    """Helper function to handle errors consistently."""
    logger.error(f"Error in {request.path}: {error_message}")
    messages.error(request, error_message)
    if redirect_url:
        return redirect(redirect_url)
    # If no redirect_url is specified, render an error template
    return render(request, 'main/error.html', {'error_message': error_message})

@cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    """Home page view."""
    try:
        latest_posts = Post.objects.filter(
            status='published'
        ).select_related('author').order_by('-created')[:3]
        return render(request, 'main/home.html', {'latest_posts': latest_posts})
    except Exception as e:
        # Instead of redirecting, render the home template with an error message
        return render(request, 'main/home.html', {
            'latest_posts': [],
            'error_message': 'Error loading latest posts.'
        })

def about(request):
    """About page view."""
    try:
        page = get_object_or_404(Page, slug='about', is_published=True)
        about_page = get_object_or_404(AboutPage, page=page)
        return render(request, 'main/about.html', {'about_page': about_page})
    except ObjectDoesNotExist:
        return handle_error(request, 'About page is currently unavailable.')
    except Exception as e:
        return handle_error(request, 'An unexpected error occurred.')

def academics(request):
    """Academics page view."""
    try:
        page = get_object_or_404(Page, slug='academics', is_published=True)
        academics_page = get_object_or_404(AcademicsPage, page=page)
        return render(request, 'main/academics.html', {'academics_page': academics_page})
    except ObjectDoesNotExist:
        return handle_error(request, 'Academics page is currently unavailable.')
    except Exception as e:
        return handle_error(request, 'An unexpected error occurred.')

def curriculum(request):
    """Curriculum page view."""
    try:
        pages = Page.objects.filter(
            slug__startswith='curriculum-',
            is_published=True
        ).select_related('curriculum_page')
        
        curriculum_pages = CurriculumPage.objects.filter(
            page__in=pages
        ).order_by('grade_level')
        
        return render(request, 'main/curriculum.html', {
            'curriculum_pages': curriculum_pages
        })
    except Exception as e:
        return handle_error(request, 'Error loading curriculum information.')

def student_life(request):
    """Student Life page view."""
    try:
        page = get_object_or_404(Page, slug='student-life', is_published=True)
        student_life_page = get_object_or_404(StudentLifePage, page=page)
        return render(request, 'main/student_life.html', {
            'student_life_page': student_life_page
        })
    except ObjectDoesNotExist:
        return handle_error(request, 'Student Life page is currently unavailable.')
    except Exception as e:
        return handle_error(request, 'An unexpected error occurred.')

class NewsListView(ListView):
    """News page view using class-based view."""
    model = Post
    template_name = 'main/news.html'
    context_object_name = 'latest_posts'
    paginate_by = 5
    
    def get_queryset(self):
        return Post.objects.filter(
            status='published'
        ).select_related('author').order_by('-created')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Latest News'
        return context

class FAQListView(ListView):
    """FAQ page view using class-based view."""
    model = FAQ
    template_name = 'main/parents.html'
    context_object_name = 'faqs'
    paginate_by = 10
    
    def get_queryset(self):
        return FAQ.objects.filter(
            is_published=True
        ).order_by('order', 'created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Frequently Asked Questions'
        return context

def contact(request):
    """Contact page view."""
    try:
        page = get_object_or_404(Page, slug='contact', is_published=True)
        contact_page = get_object_or_404(ContactPage, page=page)
        
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                try:
                    form.send_email()
                    messages.success(request, 'Your message has been sent successfully!')
                    return redirect('main:contact')
                except Exception as e:
                    logger.error(f"Error sending contact form: {str(e)}")
                    return handle_error(
                        request,
                        'There was an error sending your message. Please try again later.',
                        'main:contact'
                    )
        else:
            form = ContactForm()
        
        return render(request, 'main/contact.html', {
            'contact_page': contact_page,
            'form': form
        })
    except ObjectDoesNotExist:
        return handle_error(request, 'Contact page is currently unavailable.')
    except Exception as e:
        return handle_error(request, 'An unexpected error occurred.')
