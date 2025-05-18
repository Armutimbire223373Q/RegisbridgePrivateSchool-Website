from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import HomePageContent, NewsItem, Event, Notification
from .forms import HomePageContentForm, NewsItemForm, EventForm
from teachers.models import Announcement
from django.http import JsonResponse

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def manage_homepage(request):
    """View for managing home page content."""
    content, created = HomePageContent.objects.get_or_create()
    
    if request.method == 'POST':
        form = HomePageContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            content = form.save(commit=False)
            content.updated_by = request.user
            content.save()
            messages.success(request, 'Home page content updated successfully!')
            return redirect('core:manage_homepage')
    else:
        form = HomePageContentForm(instance=content)
    
    context = {
        'form': form,
        'content': content,
    }
    return render(request, 'core/manage_homepage.html', context)

@login_required
@user_passes_test(is_admin)
def manage_news(request):
    """View for managing news items."""
    news_items = NewsItem.objects.all().order_by('-date_posted')
    
    if request.method == 'POST':
        form = NewsItemForm(request.POST, request.FILES)
        if form.is_valid():
            news_item = form.save(commit=False)
            news_item.author = request.user
            news_item.save()
            messages.success(request, 'News item created successfully!')
            return redirect('core:manage_news')
    else:
        form = NewsItemForm()
    
    context = {
        'form': form,
        'news_items': news_items,
    }
    return render(request, 'core/manage_news.html', context)

@login_required
@user_passes_test(is_admin)
def edit_news(request, pk):
    """View for editing a news item."""
    news_item = get_object_or_404(NewsItem, pk=pk)
    
    if request.method == 'POST':
        form = NewsItemForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'News item updated successfully!')
            return redirect('core:manage_news')
    else:
        form = NewsItemForm(instance=news_item)
    
    context = {
        'form': form,
        'news_item': news_item,
    }
    return render(request, 'core/edit_news.html', context)

@login_required
@user_passes_test(is_admin)
def delete_news(request, pk):
    """View for deleting a news item."""
    news_item = get_object_or_404(NewsItem, pk=pk)
    news_item.delete()
    messages.success(request, 'News item deleted successfully!')
    return redirect('core:manage_news')

@login_required
@user_passes_test(is_admin)
def manage_events(request):
    """View for managing events."""
    events = Event.objects.all().order_by('start_date')
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('core:manage_events')
    else:
        form = EventForm()
    
    context = {
        'form': form,
        'events': events,
    }
    return render(request, 'core/manage_events.html', context)

@login_required
@user_passes_test(is_admin)
def edit_event(request, pk):
    """View for editing an event."""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('core:manage_events')
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
    }
    return render(request, 'core/edit_event.html', context)

@login_required
@user_passes_test(is_admin)
def delete_event(request, pk):
    """View for deleting an event."""
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, 'Event deleted successfully!')
    return redirect('core:manage_events')

def search(request):
    query = request.GET.get('q', '')
    if query:
        news_results = NewsItem.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        ).filter(is_published=True)
        
        event_results = Event.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        ).filter(end_date__gte=timezone.now())
        
        announcement_results = Announcement.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        ).filter(is_active=True)
        
        context = {
            'query': query,
            'news_results': news_results,
            'event_results': event_results,
            'announcement_results': announcement_results,
        }
    else:
        context = {'query': ''}
    
    return render(request, 'core/search_results.html', context)

@login_required
def dashboard(request):
    """Core dashboard view."""
    return render(request, 'core/dashboard.html')

@login_required
def notifications(request):
    """View for listing notifications."""
    notifications = Notification.objects.filter(
        recipient=request.user,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')
    
    return render(request, 'core/notifications.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, pk):
    """Mark a specific notification as read."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()
    return JsonResponse({'status': 'success'})

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def get_unread_count(request):
    """Get count of unread notifications."""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
        expires_at__gt=timezone.now()
    ).count()
    return JsonResponse({'count': count})