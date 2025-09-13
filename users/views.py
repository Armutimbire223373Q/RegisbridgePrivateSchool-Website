from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from .forms import UserProfileForm


@login_required
def profile(request):
    """Display user profile"""
    return render(request, "users/profile.html", {"user": request.user})


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def settings(request):
    """User settings page"""
    return render(request, "users/settings.html", {"user": request.user})


def register(request):
    """User registration"""
    if request.method == "POST":
        # Handle registration logic here
        messages.success(request, "Registration successful! Please log in.")
        return redirect("users:login")

    return render(request, "users/register.html")
