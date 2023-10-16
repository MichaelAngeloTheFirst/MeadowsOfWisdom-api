from django.contrib.auth.models import User
from mow_api.models import FunFact, FunFactComment
from mow_api.serializers import (
    FunFactSerializer,
    UserSerializer,
    FunFactCommentSerializer,
)
from rest_framework import permissions, response, status, viewsets
from django.shortcuts import get_object_or_404


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
        return response.Response(
            {"message": "successful"}, status=status.HTTP_201_CREATED
        )


class FunFactViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to perform actions on fun facts.
    """

    queryset = FunFact.objects.all()
    serializer_class = FunFactSerializer
    permission_classes = [ReadOnlyOrAuthor]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = FunFactComment.objects.all()
    serializer_class = FunFactCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    # methods from other kwargs, add case if  user is diff than author
    def get_queryset(self):
        return super().get_queryset().filter(fact=self.kwargs["fact_id"])

    def get_save_kwargs(self):
        kwargs = {}
        kwargs["fact"] = self.fact
        kwargs["author"] = self.author
        kwargs["parent"] = self.parent
        kwargs["comment_text"] = self.comment_text
        return kwargs

    @property
    def fact(self):
        fact_id = self.kwargs.get("fact_id")
        if fact_id is None:
            return None
        return get_object_or_404(FunFact, pk=fact_id)

    @property
    def author(self):
        return self.request.user

    @property
    def parent(self):
        parent_id = self.request.data.get("parent_id")
        print("parent_id", parent_id)
        if parent_id is None:
            return None
        if parent_id == "0":
            return None
        return get_object_or_404(FunFactComment, pk=parent_id)

    @property
    def comment_text(self):
        return self.request.data.get("comment_text")

    def perform_create(self, serializer):
        serializer.save(**self.get_save_kwargs())


class VotesViewSet(viewsets.ModelViewSet):
    queryset = FunFact.objects.all()
    serializer_class = FunFactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        kwargs = {}
        kwargs["fact"] = self.fact
        kwargs["author"] = self.author
        kwargs["vote"] = self.vote

    @property
    def fact(self):
        fact_id = self.kwargs.get("fact_id")
        if fact_id is None:
            return None
        return get_object_or_404(FunFact, pk=fact_id)

    @property
    def author(self):
        return self.request.user

    @property
    def vote(self):
        return self.request.data.get("vote")
