from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import Profile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "password", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email" "followers")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "user", "username", "bio", "profile_picture")
        read_only_fields = ("user",)


class ProfileDetailSerializer(serializers.ModelSerializer):
    followers = UserSerializer(
        many=True, source="user.followers", read_only=True
    )
    following = UserSerializer(
        many=True, source="user.following", read_only=True
    )

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "username",
            "bio",
            "profile_picture",
            "followers",
            "following",
        )
        read_only_fields = ("user", "followers", "following")
