from functools import wraps
from typing import Callable, Iterable

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def role_required(
    allowed_roles: Iterable[str], redirect_to: str = "dashboard:main"
) -> Callable:
    """Decorator enforcing that the authenticated user has one of the allowed roles.

    Args:
        allowed_roles: Iterable of role strings as defined on users.models.User.Role
        redirect_to: Named URL to redirect unauthorized users
    """

    def decorator(view_func: Callable) -> Callable:
        @login_required
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user_role = getattr(request.user, "role", None)
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(
                request, "Access denied. You do not have permission to view this page."
            )
            return redirect(redirect_to)

        return _wrapped

    return decorator


class RoleRequiredMixin:
    """Class-based-view mixin to enforce role membership."""

    allowed_roles: Iterable[str] = ()
    redirect_to: str = "dashboard:main"

    @classmethod
    def as_view(cls, **initkwargs):  # type: ignore[override]
        view = super().as_view(**initkwargs)
        return role_required(cls.allowed_roles, cls.redirect_to)(view)





