from rest_framework import routers
from django.urls import path, include
from api.views import PostViewSet, HashtagViewSet

app_name = "api"
router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")
router.register("tags", HashtagViewSet, basename="hashtags")
urlpatterns = [
    path("", include(router.urls)),
]
