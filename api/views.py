from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
)
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Post, Like, Hashtag
from api.serializers import (
    CommentSerializer,
    PostSerializer,
    HashtagSerializer,
    PostDetailSerializer,
)
from api.permissions import IsAuthorOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of posts",
        description=(
            "Retrieve a list of all posts "
            "by the authenticated user and the "
            "users they follow."
        ),
        responses={200: PostSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Post list example",
                value=[
                    {
                        "id": 1,
                        "author": {"id": 1, "username": "user1"},
                        "content": "This is a post",
                        "created": "2024-06-18T12:34:56Z",
                        "image": "https://example.com/media/post1.jpg",
                    }
                ],
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single post",
        description="Retrieve the details of a specific post by its ID.",
        responses={200: PostDetailSerializer},
        examples=[
            OpenApiExample(
                "Post detail example",
                value={
                    "id": 1,
                    "author": {"id": 1, "username": "user1"},
                    "content": "This is a post",
                    "created": "2024-06-18T12:34:56Z",
                    "image": "https://example.com/media/post1.jpg",
                    "comments": [
                        {
                            "id": 1,
                            "author": {"id": 2, "username": "user2"},
                            "content": "Nice post!",
                            "created": "2024-06-18T13:00:00Z",
                        }
                    ],
                },
            )
        ],
    ),
    create=extend_schema(
        summary="Create a new post",
        description=(
            "Create a new post. Only authenticated " "users can create posts."
        ),
        responses={201: PostSerializer},
        examples=[
            OpenApiExample(
                "Create post example",
                value={"content": "This is a new post", "image": None},
            )
        ],
    ),
)
class PostViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        IsAuthenticated,
        IsAuthorOrReadOnly,
    )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        following_users = user.following.all()
        return Post.objects.filter(
            Q(author=user) | Q(author__in=following_users)
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        return self.serializer_class

    @extend_schema(
        summary="Like or unlike a post",
        description=(
            "Toggle like on a post. Only authenticated "
            "users can like/unlike posts."
        ),
        request=None,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Like response",
                        value={"status": "liked"},
                    ),
                    OpenApiExample(
                        "Unlike response",
                        value={"status": "unliked"},
                    ),
                ],
            ),
        },
    )
    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            author=request.user, post=post
        )
        if not created:
            like.delete()
            return Response({"status": "unliked"}, status=status.HTTP_200_OK)
        return Response({"status": "liked"}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Comment on a post",
        description=(
            "Add a comment to a post. Only authenticated "
            "users can comment on posts."
        ),
        request=CommentSerializer,
        responses={
            201: CommentSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Invalid data response",
                        value={"detail": "Invalid data."},
                    )
                ],
            ),
        },
    )
    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def comment(self, request, pk=None):
        print("Hello")
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        print(self.kwargs.get("content"))
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of hashtags",
        description=(
            "Retrieve a list of all hashtags. "
            "Accessible by authenticated users."
        ),
        responses={200: HashtagSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Hashtag list example",
                value=[
                    {"id": 1, "name": "#example"},
                    {"id": 2, "name": "#hashtag"},
                ],
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single hashtag",
        description=(
            "Retrieve the details of a specific "
            "hashtag by its ID. "
            "Accessible by authenticated users."
        ),
        responses={200: HashtagSerializer},
        examples=[
            OpenApiExample(
                "Hashtag detail example",
                value={"id": 1, "name": "#example"},
            )
        ],
    ),
    create=extend_schema(
        summary="Create a new hashtag",
        description=(
            "Create a new hashtag. Only authenticated "
            "users can create hashtags."
        ),
        responses={201: HashtagSerializer},
        examples=[
            OpenApiExample(
                "Create hashtag example",
                value={"name": "#newhashtag"},
            )
        ],
    ),
)
class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)
