from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from core.models import HomePageContent, NewsItem, Event
from django.utils import timezone
from django.db.models import Q

@cache_page(60 * 15)  # Cache for 15 minutes
@vary_on_cookie  # Vary cache by user session
def home(request):
    """View for the home page with improved caching and error handling."""
    try:
        # Try to get content from cache
        content = cache.get('homepage_content')
        if content is None:
            content = HomePageContent.objects.first()
            if content:
                cache.set('homepage_content', content, 60 * 30)  # Cache for 30 minutes
        
        # Get active news items
        news_items = NewsItem.objects.filter(
            Q(is_published=True)
        ).select_related('author').order_by('-date_posted')[:3]
        
        # Get upcoming events
        now = timezone.now()
        events = Event.objects.filter(
            Q(end_date__gte=now) |
            Q(start_date__gte=now)
        ).select_related('created_by').order_by('start_date')[:3]
        
        context = {
            'content': content,
            'news_items': news_items,
            'events': events,
        }
        
    except Exception as e:
        # Log the error (you should configure proper logging)
        print(f"Error in homepage view: {str(e)}")
        # Provide minimal context with empty data
        context = {
            'content': None,
            'news_items': [],
            'events': [],
            'error': "We're experiencing technical difficulties. Please try again later."
        }
    
    return render(request, 'homepage/home.html', context)
