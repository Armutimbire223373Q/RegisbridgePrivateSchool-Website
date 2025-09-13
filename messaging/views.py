from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Thread, Message


@login_required
def inbox(request):
    threads = (
        Thread.objects.filter(participants=request.user)
        .order_by("-created_at")
        .distinct()
    )
    return render(request, "messaging/inbox.html", {"threads": threads})


@login_required
def thread_view(request, thread_id: int):
    thread = get_object_or_404(
        Thread.objects.prefetch_related("messages", "participants"), id=thread_id
    )
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(thread=thread, sender=request.user, content=content)
            messages.success(request, "Message sent.")
            return redirect(reverse("thread_view", args=[thread.id]))
    msgs = thread.messages.select_related("sender").all()
    return render(
        request, "messaging/thread.html", {"thread": thread, "messages": msgs}
    )


@login_required
def compose(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        participants = [request.user]
        thread = Thread.objects.create(title=title, created_by=request.user)
        thread.participants.add(*participants)
        content = request.POST.get("content", "")
        if content:
            Message.objects.create(thread=thread, sender=request.user, content=content)
        messages.success(request, "Thread created.")
        return redirect(reverse("thread_view", args=[thread.id]))
    return render(request, "messaging/compose.html")
