from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")

    # def to_representation(self, instance):
    #     return super().to_representation(instance)


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "last_login",
            "created_at",
        )
        read_only_fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "blocked_at",
            "last_login",
            "created_at",
        )
