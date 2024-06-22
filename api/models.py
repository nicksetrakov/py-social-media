import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


def post_image_file_path(instance: "Post", filename: str) -> str:
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/post-pictures/", filename)


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hashtags = models.ManyToManyField(
        "Hashtag", related_name="posts", blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"title: {self.title}, content: {self.content}"


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return str(self.name)


class Comment(models.Model):
    content = models.TextField()
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.CASCADE
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-updated_at"]

    def __str__(self) -> str:
        return str(self.content)


class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, related_name="likes", on_delete=models.CASCADE, null=True
    )
    comment = models.ForeignKey(
        Comment, related_name="likes", on_delete=models.CASCADE, null=True
    )

    class Meta:
        verbose_name_plural = "likes"
        unique_together = ("author", "post") or ("author", "comment")

    def __str__(self) -> str:
        return str(self.author)
