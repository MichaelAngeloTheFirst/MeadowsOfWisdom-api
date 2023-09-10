from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, generics, status, response
from mow_api.serializers import UserSerializer, GroupSerializer, FunFactSerializer
from mow_api.models import FunFact


class ReadOnlyOrAuthor(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True and self.has_permission(request, view)

        return obj.author == request.user and self.has_permission(request, view)


class IsPostRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method == "POST"


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to perform actions on users.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated | IsPostRequest]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return response.Response({"message": "successful"}, status=status.HTTP_201_CREATED)


class FunFactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to perform actions on fun facts.
    """

    queryset = FunFact.objects.all()
    serializer_class = FunFactSerializer
    permission_classes = [ReadOnlyOrAuthor]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
