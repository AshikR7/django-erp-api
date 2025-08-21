from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role_name', 'employee_id',
            'phone_number', 'department'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")

        # Validate role exists
        role_name = attrs['role_name']
        if not Role.objects.filter(name=role_name).exists():
            raise serializers.ValidationError(f"Role '{role_name}' does not exist")

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        role_name = validated_data.pop('role_name')
        password = validated_data.pop('password')

        role = Role.objects.get(name=role_name)
        user = User.objects.create_user(
            password=password,
            role=role,
            **validated_data
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role.name if self.user.role else None,
            'employee_id': self.user.employee_id,
        }

        return data


class UserListSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    manager = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'employee_id', 'phone_number', 'department',
            'manager', 'is_active', 'created_at'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    manager = UserListSerializer(read_only=True)
    subordinates = UserListSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'employee_id', 'phone_number', 'department',
            'manager', 'subordinates', 'is_active', 'created_at', 'updated_at'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'department',
            'role_name', 'is_active', 'employee_id'
        ]

    def validate_role_name(self, value):
        if value and not Role.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Role '{value}' does not exist")
        return value

    def update(self, instance, validated_data):
        role_name = validated_data.pop('role_name', None)

        if role_name:
            role = Role.objects.get(name=role_name)
            instance.role = role

        return super().update(instance, validated_data)