from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    extend_schema_view,
    OpenApiParameter,
)
from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

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


@extend_schema(
    summary="Create a new user",
    description="Create a new user. This endpoint is publicly accessible.",
    request=UserSerializer,
    responses={
        201: UserSerializer,
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
    examples=[
        OpenApiExample(
            "Create user example",
            value={
                "email": "newuser@example.com",
                "password": "newpassword",
                "is_staff": False,
            },
        )
    ],
)
class CreateUserView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of profiles",
        description=(
            "Retrieve a list of all profiles. "
            "You can search by email or username using "
            "the 'search' query parameter."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                description=(
                    "Search users by email or username. " "(ex. ?search=user)"
                ),
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: ProfileSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Profile list example",
                value=[
                    {
                        "id": 1,
                        "username": "user1",
                        "email": "user1@example.com",
                        "bio": "This is user1's bio",
                    },
                    {
                        "id": 2,
                        "username": "user2",
                        "email": "user2@example.com",
                        "bio": "This is user2's bio",
                    },
                ],
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a single profile",
        description="Retrieve the details of a specific profile by its ID.",
        responses={200: ProfileDetailSerializer},
        examples=[
            OpenApiExample(
                "Profile detail example",
                value={
                    "id": 1,
                    "username": "user1",
                    "email": "user1@example.com",
                    "bio": "This is user1's bio",
                    "followers": [
                        {
                            "id": 2,
                            "username": "user2",
                            "email": "user2@example.com",
                        },
                    ],
                    "following": [
                        {
                            "id": 3,
                            "username": "user3",
                            "email": "user3@example.com",
                        },
                    ],
                },
            )
        ],
    ),
    create=extend_schema(
        summary="Create a new profile",
        description=(
            "Create a new profile. Only authenticated "
            "users can create profiles."
        ),
        responses={201: ProfileSerializer},
        examples=[
            OpenApiExample(
                "Create profile example",
                value={
                    "bio": "This is my bio",
                },
            )
        ],
    ),
)
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, IsProfileOwnerOrReadOnly)

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

    @extend_schema(
        summary="Follow a user",
        description=(
            "Follow a user. Only authenticated "
            "users can follow other users."
        ),
        request=None,
        responses={
            201: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Follow response",
                        value={"detail": "Successfully followed user"},
                    )
                ],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Already following response",
                        value={"detail": "Already following"},
                    ),
                    OpenApiExample(
                        "Follow self response",
                        value={"detail": "You cannot follow yourself"},
                    ),
                ],
            ),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated,
        ],
    )
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

    @extend_schema(
        summary="Unfollow a user",
        description=(
            "Unfollow a user. Only authenticated"
            " users can unfollow other users."
        ),
        request=None,
        responses={
            204: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Unfollow response",
                        value={"detail": "Successfully unfollowed user"},
                    )
                ],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Not following response",
                        value={"detail": "Not following"},
                    ),
                ],
            ),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticated,
        ],
    )
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

    @extend_schema(
        summary="Get followers of a user",
        description=(
            "Retrieve the list of followers " "for the authenticated user."
        ),
        responses={200: UserSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Followers list example",
                value=[
                    {
                        "id": 1,
                        "username": "user1",
                        "email": "user1@example.com",
                    },
                    {
                        "id": 2,
                        "username": "user2",
                        "email": "user2@example.com",
                    },
                ],
            )
        ],
    )
    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        user = self.request.user
        followers = user.followers.all()
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get following users",
        description=(
            "Retrieve the list of users that "
            "the authenticated user is following."
        ),
        responses={200: UserSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Following list example",
                value=[
                    {
                        "id": 3,
                        "username": "user3",
                        "email": "user3@example.com",
                    },
                    {
                        "id": 4,
                        "username": "user4",
                        "email": "user4@example.com",
                    },
                ],
            )
        ],
    )
    @action(detail=True, methods=["get"])
    def following(self, request, pk=None):
        user = self.request.user
        following = user.following.all()
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data)
