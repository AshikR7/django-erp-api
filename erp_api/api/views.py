from django.shortcuts import render

# Create your views here.


from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.db.models import Q
from .models import User, Role
from .serializers import (
    UserRegistrationSerializer, CustomTokenObtainPairSerializer,
    UserListSerializer, UserDetailSerializer, UserUpdateSerializer
)
from .permissions import IsAdminUser, IsManagerOrAdmin, CanManageUser, IsOwnerOrAdmin


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAdminUser]  # Only admins can create users

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.name
            }
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view with additional user info"""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout view - blacklist refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        logout(request)
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """List all users - Admin and Manager only"""
    serializer_class = UserListSerializer
    permission_classes = [IsManagerOrAdmin]

    def get_queryset(self):
        queryset = User.objects.select_related('role', 'manager')

        # Managers can only see employees and other managers (not admins)
        if self.request.user.is_manager:
            queryset = queryset.filter(~Q(role__name='admin'))

        # Filter by role if specified
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role__name=role)

        # Filter by department if specified
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)

        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )

        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """User detail view with role-based permissions"""
    queryset = User.objects.select_related('role', 'manager').prefetch_related('subordinates')
    permission_classes = [CanManageUser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailSerializer
        return UserUpdateSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Managers cannot access admin users
        if self.request.user.is_manager:
            queryset = queryset.filter(~Q(role__name='admin'))

        return queryset

    def perform_destroy(self, instance):
        # Soft delete - just deactivate the user
        instance.is_active = False
        instance.save()


class ProfileView(generics.RetrieveUpdateAPIView):
    """Current user profile view"""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserDetailSerializer
        return UserUpdateSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Dashboard statistics - role-based data"""
    user = request.user
    stats = {}

    if user.is_admin:
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'admins_count': User.objects.filter(role__name='admin').count(),
            'managers_count': User.objects.filter(role__name='manager').count(),
            'employees_count': User.objects.filter(role__name='employee').count(),
        }
    elif user.is_manager:
        stats = {
            'team_size': User.objects.filter(manager=user).count(),
            'department_users': User.objects.filter(
                department=user.department
            ).count() if user.department else 0,
        }
    else:  # Employee
        stats = {
            'profile_completion': 100,  # Calculate based on filled fields
        }

    return Response(stats)