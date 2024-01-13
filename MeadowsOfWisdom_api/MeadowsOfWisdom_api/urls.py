from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from mow_api import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"funfacts", views.FunFactViewSet, basename="funfacts_test")
router.register(r"register", views.UserViewSet, basename="register_test")
router.register(r"users", views.UserViewSet, basename="user_test")
router.register(
    r"funfacts/(?P<fact_id>\d+)/comments",
    views.CommentsViewSet,
    basename="comments_test",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    re_path(r"api/token/refresh/?", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"api/token/?", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(
        r"api/(?P<comment_id>\d+)/comments/(?P<vote_value>[a-z]+)/votes/?$",
        view=views.CommentVotesView.as_view(),
        name="comment_votes",
    ),
    re_path(
        r"api/(?P<fact_id>\d+)/facts/(?P<vote_value>[a-z]+)/votes/?$",
        view=views.FactVotesView.as_view(),
        name="fact_votes",
    ),
]
