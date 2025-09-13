from typing import Dict

from django.http import HttpRequest

from .models import UserNotification


def unread_notifications(request: HttpRequest) -> Dict[str, int]:
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {"unread_notifications": 0}

    count = UserNotification.objects.filter(user=request.user, is_read=False).count()
    return {"unread_notifications": count}





