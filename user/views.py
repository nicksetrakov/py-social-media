from django.db.models import Q
from rest_framework import viewsets, permissions, generics
from rest_framework.generics import CreateAPIView

from user.permissions import IsProfileOwnerOrReadOnly
from .models import User, Profile
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    ProfileDetailSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, mixins


class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class ProfileViewSet(
    viewsets.ModelViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, IsProfileOwnerOrReadOnly)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProfileDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            search_query = self.request.query_params.get("search", None)
            if search_query:
                queryset = queryset.filter(
                    Q(user__email__icontains=search_query)
                    | Q(username__icontains=search_query)
                )
        return queryset

    @action(detail=True, methods=["post"])
    def follow(self, request, pk=None):
        profile = self.get_object()
        user_to_follow = profile.user
        user = request.user
        if user != user_to_follow:
            if not user.following.filter(id=user_to_follow.id).exists():
                user.following.add(user_to_follow)
                return Response(
                    status=status.HTTP_201_CREATED,
                    data={"detail": "Successfully followed user"},
                )
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Already following"},
            )
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": "You cannot follow yourself"},
        )

    @action(detail=True, methods=["post"])
    def unfollow(self, request, pk=None):
        profile = self.get_object()
        user_to_unfollow = profile.user
        user = request.user
        if user.following.filter(id=user_to_unfollow.id).exists():
            user.following.remove(user_to_unfollow)
            return Response(
                status=status.HTTP_204_NO_CONTENT,
                data={"detail": "Successfully unfollowed user"},
            )
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"detail": "Not following"},
        )

    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        user = self.request.user
        followers = user.followers.all()
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def following(self, request, pk=None):
        user = self.request.user
        following = user.following.all()
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data)
