from rest_framework import serializers

from user.serializers import UserSerializer
from .models import Post, Like, Comment, Hashtag


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "author", "post", "content", "created_at")
        read_only_fields = ("author", "post", "created_at")


class LikeSerializer(serializers.ModelSerializer):
    author = UserSerializer()

    class Meta:
        model = Like
        fields = ("id", "author",)
        read_only_fields = ("author",)


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "image",
            "created_at",
            "hashtags",
        )
        read_only_fields = ("author",)


class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    hashtags = serializers.SlugRelatedField(
        many=True,
        queryset=Hashtag.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "image",
            "created_at",
            "hashtags",
            "comments",
            "likes",
        )
        read_only_fields = ("author", "comments", "likes")
