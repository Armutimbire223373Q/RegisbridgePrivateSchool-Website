from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q, Count, Max, Exists, OuterRef
from django.contrib import messages
from django.urls import reverse_lazy
from .models import (
    MessageThread, Message, MessageAttachment, MessageRecipient,
    Announcement, AnnouncementRecipient
)
from .forms import MessageForm, AnnouncementForm, MessageThreadForm

class InboxView(LoginRequiredMixin, ListView):
    """Display user's message threads"""
    model = MessageThread
    template_name = 'messaging/inbox.html'
    context_object_name = 'threads'
    paginate_by = 20

    def get_queryset(self):
        return (MessageThread.objects
                .filter(participants=self.request.user, archived=False)
                .annotate(unread_count=Count(
                    'messages__recipients',
                    filter=Q(
                        messages__recipients__user=self.request.user,
                        messages__recipients__read_at__isnull=True,
                        messages__recipients__deleted=False
                    )
                ))
                .annotate(last_message_time=Max('messages__sent_at'))
                .order_by('-last_message_time'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['archived_count'] = (MessageThread.objects
                                   .filter(participants=self.request.user, archived=True)
                                   .count())
        return context

class ThreadDetailView(LoginRequiredMixin, DetailView):
    """Display a message thread and its messages"""
    model = MessageThread
    template_name = 'messaging/thread_detail.html'
    context_object_name = 'thread'

    def get_queryset(self):
        return MessageThread.objects.filter(participants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = MessageForm()
        
        # Mark messages as read
        MessageRecipient.objects.filter(
            message__thread=self.object,
            user=self.request.user,
            read_at__isnull=True
        ).update(read_at=timezone.now())
        
        return context

@login_required
def create_thread(request):
    """Create a new message thread"""
    if request.method == 'POST':
        form = MessageThreadForm(request.POST)
        if form.is_valid():
            thread = form.save()
            thread.participants.add(request.user, *form.cleaned_data['participants'])
            
            # Create the first message
            message = Message.objects.create(
                thread=thread,
                sender=request.user,
                body=form.cleaned_data['initial_message']
            )
            
            # Create recipient records
            for participant in thread.participants.all():
                MessageRecipient.objects.create(
                    message=message,
                    user=participant,
                    read_at=timezone.now() if participant == request.user else None
                )
            
            messages.success(request, 'Message sent successfully.')
            return redirect('messaging:thread_detail', pk=thread.pk)
    else:
        form = MessageThreadForm()
    
    return render(request, 'messaging/create_thread.html', {'form': form})

@login_required
def send_message(request, thread_id):
    """Add a message to an existing thread"""
    thread = get_object_or_404(MessageThread, pk=thread_id, participants=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()
            
            # Handle attachments
            for uploaded_file in request.FILES.getlist('attachments'):
                MessageAttachment.objects.create(
                    message=message,
                    file=uploaded_file,
                    filename=uploaded_file.name,
                    file_size=uploaded_file.size
                )
            
            # Create recipient records
            for participant in thread.participants.all():
                MessageRecipient.objects.create(
                    message=message,
                    user=participant,
                    read_at=timezone.now() if participant == request.user else None
                )
            
            # Update thread timestamp
            thread.updated_at = timezone.now()
            thread.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('messaging:thread_detail', pk=thread_id)
    
    return HttpResponseForbidden()

class AnnouncementListView(LoginRequiredMixin, ListView):
    """Display list of announcements"""
    model = Announcement
    template_name = 'messaging/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        base_query = Announcement.objects.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

        # Filter based on user role
        if user.groups.filter(name='Teachers').exists():
            base_query = base_query.filter(
                Q(recipient_group__in=['all', 'staff', 'teachers'])
            )
        elif user.groups.filter(name='Students').exists():
            base_query = base_query.filter(
                Q(recipient_group__in=['all', 'students'])
            )
        elif user.groups.filter(name='Parents').exists():
            base_query = base_query.filter(
                Q(recipient_group__in=['all', 'parents'])
            )
        else:  # Staff
            base_query = base_query.filter(
                Q(recipient_group__in=['all', 'staff'])
            )

        # Annotate with read status
        return base_query.annotate(
            is_read=Exists(
                AnnouncementRecipient.objects.filter(
                    announcement=OuterRef('pk'),
                    user=user,
                    read_at__isnull=False
                )
            )
        ).order_by('-priority', '-created_at')

class AnnouncementCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new announcement"""
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'messaging/announcement_form.html'
    success_url = reverse_lazy('messaging:announcement_list')

    def test_func(self):
        """Only staff and teachers can create announcements"""
        return self.request.user.groups.filter(name__in=['Staff', 'Teachers']).exists()

    def form_valid(self, form):
        form.instance.sender = self.request.user
        response = super().form_valid(form)
        
        # Send notifications if enabled
        if form.instance.send_email:
            # TODO: Implement email sending
            pass
        
        if form.instance.send_sms:
            # TODO: Implement SMS sending
            pass
        
        messages.success(self.request, 'Announcement created successfully.')
        return response

@login_required
def mark_announcement_read(request, pk):
    """Mark an announcement as read"""
    announcement = get_object_or_404(Announcement, pk=pk)
    AnnouncementRecipient.objects.get_or_create(
        announcement=announcement,
        user=request.user,
        defaults={'read_at': timezone.now()}
    )
    return JsonResponse({'status': 'success'})

@login_required
def archive_thread(request, pk):
    """Archive/unarchive a message thread"""
    thread = get_object_or_404(MessageThread, pk=pk, participants=request.user)
    thread.archived = not thread.archived
    thread.save()
    action = 'archived' if thread.archived else 'unarchived'
    messages.success(request, f'Thread {action} successfully.')
    return redirect('messaging:inbox')
