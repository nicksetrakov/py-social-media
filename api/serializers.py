from django.utils import timezone
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
        fields = (
            "id",
            "author",
        )
        read_only_fields = ("author",)


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class PostSerializer(serializers.ModelSerializer):
    schedule_time = serializers.DateTimeField(required=False)

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "image",
            "created_at",
            "hashtags",
            "schedule_time",
            "published"
        )
        read_only_fields = ("author", "published")

    def validate_schedule_time(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future."
            )
        return value

    def create(self, validated_data):
        schedule_time = validated_data.pop("schedule_time", None)
        hashtags_data = validated_data.pop("hashtags", None)
        post = Post(**validated_data)
        post.save()
        if hashtags_data:
            post.hashtags.set(hashtags_data)

        if schedule_time:
            from .tasks import create_scheduled_post
            post.published = False
            post.save()
            create_scheduled_post.apply_async(
                (
                    post.pk,
                ),
                eta=schedule_time,
            )
        return post


class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    hashtags = serializers.SlugRelatedField(
        many=True, queryset=Hashtag.objects.all(), slug_field="name"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "content",
            "image",
            "created_at",
            "hashtags",
            "comments",
            "likes",
            "published",
        )
        read_only_fields = ("author", "comments", "likes", "published")
