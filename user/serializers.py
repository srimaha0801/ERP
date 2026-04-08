from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    role = serializers.ChoiceField(
        choices=['admin', 'manager', 'user'],
        write_only=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role')

        user = User.objects.create_user(**validated_data)

        # Assign role for users
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'manager':
            user.is_staff = True
        else:
            user.is_staff = False
            user.is_superuser = False

        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']