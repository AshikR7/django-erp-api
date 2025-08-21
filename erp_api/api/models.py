from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Role(models.Model):
    """Role model for RBAC"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Extended User model with role-based access"""
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users',
                            null=True, blank=True)  # Allow null during creation
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='subordinates')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def clean(self):
        """Custom validation"""
        super().clean()

        # Manager cannot be assigned to themselves
        if self.manager and self.manager == self:
            raise ValidationError("User cannot be their own manager")

        # Admin users cannot have managers (only check if role exists)
        if self.role and self.role.name == 'admin' and self.manager:
            raise ValidationError("Admin users cannot have managers")

    def save(self, *args, **kwargs):
        # Skip full_clean for superuser creation if no role is set
        if not (self.is_superuser and not self.role):
            self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self):
        return self.role and self.role.name == 'admin'

    @property
    def is_manager(self):
        return self.role and self.role.name == 'manager'

    @property
    def is_employee(self):
        return self.role and self.role.name == 'employee'

    def can_manage_user(self, user):
        """Check if current user can manage another user"""
        if self.is_admin:
            return True
        elif self.is_manager:
            return not user.is_admin
        return False


class UserSession(models.Model):
    """Track user sessions for security"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    token_jti = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_sessions'
        ordering = ['-created_at']