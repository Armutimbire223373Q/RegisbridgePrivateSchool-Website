from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_active')
    list_filter = ('is_student', 'is_teacher', 'is_parent', 'is_staff_member', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'date_of_birth',
                                       'phone_number', 'address', 'profile_picture')}),
        (_('User type'), {'fields': ('is_student', 'is_teacher', 'is_parent', 'is_staff_member')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                     'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    def get_user_type(self, obj):
        types = []
        if obj.is_student:
            types.append('Student')
        if obj.is_teacher:
            types.append('Teacher')
        if obj.is_parent:
            types.append('Parent')
        if obj.is_staff_member:
            types.append('Staff')
        return ', '.join(types) if types else 'No type set'
    get_user_type.short_description = _('User Type')
