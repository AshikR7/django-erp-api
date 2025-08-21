from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserSession


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['name', 'created_at']
    search_fields = ['name', 'description']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'full_name', 'role', 'department', 'is_active', 'created_at']
    list_filter = ['role', 'department', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Department', {
            'fields': ('role', 'employee_id', 'department', 'manager')
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['token_jti', 'created_at']