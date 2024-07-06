from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import Post, Hashtag, Comment, Like
from api.serializers import (
    PostSerializer,
    CommentSerializer,
    LikeSerializer,
    HashtagSerializer,
)
from django.contrib.auth import get_user_model


POST_LIST_URL = reverse("api:posts-list")
HASHTAG_LIST_URL = reverse("api:hashtags-list")

User = get_user_model()


class PostSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpass"
        )
        self.post_attributes = {
            "title": "Test Post",
            "content": "This is a test post.",
            "author": self.user,
            "published": True,
        }
        self.serializer_data = {
            "title": "Test Post",
            "content": "This is a test post.",
            "author": self.user.id,
            "published": True,
        }
        self.post = Post.objects.create(**self.post_attributes)
        self.serializer = PostSerializer(instance=self.post)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(),
            [
                "id",
                "author",
                "title",
                "content",
                "image",
                "created_at",
                "hashtags",
                "published",
            ],
        )

    def test_title_field_content(self):
        data = self.serializer.data
        self.assertEqual(data["title"], self.post_attributes["title"])


class CommentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpass"
        )
        self.post = Post.objects.create(
            title="Test Post", content="This is a test post.", author=self.user
        )
        self.comment_attributes = {
            "content": "This is a comment.",
            "post": self.post,
            "author": self.user,
        }
        self.serializer_data = {
            "content": "This is a comment.",
            "post": self.post.id,
            "author": self.user.id,
        }
        self.comment = Comment.objects.create(**self.comment_attributes)
        self.serializer = CommentSerializer(instance=self.comment)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(), ["id", "author", "post", "content", "created_at"]
        )

    def test_content_field_content(self):
        data = self.serializer.data
        self.assertEqual(data["content"], self.comment_attributes["content"])


class LikeSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpass"
        )
        self.post = Post.objects.create(
            title="Test Post", content="This is a test post.", author=self.user
        )
        self.like = Like.objects.create(author=self.user, post=self.post)
        self.serializer = LikeSerializer(instance=self.like)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ["id", "author"])

    def test_author_field_content(self):
        data = self.serializer.data
        self.assertEqual(data["author"]["email"], self.user.email)


class HashtagSerializerTest(TestCase):
    def setUp(self):
        self.hashtag = Hashtag.objects.create(name="#test")
        self.serializer = HashtagSerializer(instance=self.hashtag)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ["id", "name"])

    def test_name_field_content(self):
        data = self.serializer.data
        self.assertEqual(data["name"], self.hashtag.name)


class PostViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpass"
        )
        self.client.force_authenticate(self.user)
        self.post = Post.objects.create(
            title="Test Post", content="This is a test post.", author=self.user
        )

    def test_list_posts(self):
        response = self.client.get(POST_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_post(self):
        url = reverse("api:posts-detail", kwargs={"pk": self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        data = {
            "title": "New Post",
            "content": "This is a new post.",
            "author": self.user.id,
        }
        response = self.client.post(POST_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_like_post(self):
        url = reverse("api:posts-like", kwargs={"pk": self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "liked")

    def test_unlike_post(self):
        url = reverse("api:posts-like", kwargs={"pk": self.post.pk})
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "unliked")

    def test_create_comment(self):
        url = reverse("api:posts-comment", kwargs={"pk": self.post.pk})
        data = {
            "content": "This is a new comment.",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], data["content"])


class HashtagViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpass"
        )
        self.client.force_authenticate(self.user)
        self.hashtag = Hashtag.objects.create(name="#test")

    def test_list_hashtags(self):
        response = self.client.get(HASHTAG_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_hashtag(self):
        url = reverse("api:hashtags-detail", kwargs={"pk": self.hashtag.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_hashtag(self):
        data = {"name": "#newhashtag"}
        response = self.client.post(HASHTAG_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpass"
        )
        self.other_user = User.objects.create_user(
            email="otheruser@gmail.com", password="otherpass"
        )
        self.post = Post.objects.create(
            title="Test Post", content="This is a test post.", author=self.user
        )

    def test_post_creation_permission(self):
        data = {
            "title": "Unauthorized Post",
            "content": "This should not be allowed.",
            "author": self.user.id,
        }
        response = self.client.post(POST_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_creation_permission(self):
        url = reverse("api:posts-comment", kwargs={"pk": self.post.pk})
        data = {
            "content": "Unauthorized comment.",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_like_creation_permission(self):
        url = reverse("api:posts-like", kwargs={"pk": self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
