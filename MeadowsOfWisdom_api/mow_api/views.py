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


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class CreateUserViewSet(generics.CreateAPIView):
    """
    API endpoint that creates users.
    """

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]  # Or anon users can't register
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            {"message": "success"}, status=status.HTTP_201_CREATED, headers=headers
        )


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class FunFactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows FunFacts to be viewed.
    """

    queryset = FunFact.objects.all()
    serializer_class = FunFactSerializer
    permission_classes = [ReadOnlyOrAuthor]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
