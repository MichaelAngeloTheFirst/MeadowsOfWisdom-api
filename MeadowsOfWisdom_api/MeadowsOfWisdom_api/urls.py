"""
URL configuration for MeadowsOfWisdom_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from mow_api import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"funfacts", views.FunFactViewSet)
router.register(r"register", views.UserViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"funfacts/(?P<fact_id>\d+)/comments/?$", views.CommentsViewSet)
router.register(
    r"funfacts/(?P<fact_id>\d+)/votes/?$",
    views.VotesViewSet,
)
# TO DO: consider adding routes for votes/comments votes/funfacts

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    re_path(r"api/token/refresh/?", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"api/token/?", TokenObtainPairView.as_view(), name="token_obtain_pair"),
]
