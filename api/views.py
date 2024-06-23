from django.db.models import Q
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


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)
