from django.contrib.auth.models import User
from django.http import Http404
from mow_api.models import FunFact, FunFactComment, FunFactVote  # , FunFactVote
from mow_api.serializers import (
    FunFactSerializer,
    UserSerializer,
    FunFactCommentSerializer,
)
from rest_framework import permissions, response, status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from django.db import IntegrityError


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

    def get_serializer_context(self):
        return {"request": self.request}

    @property
    def author(self):
        return self.request.user

    @property
    def fact_text(self):
        return self.request.data.get("fact_text")

    def get_save_kwargs(self):
        kwargs = {}
        kwargs["author"] = self.author
        kwargs["fact_text"] = self.fact_text
        return kwargs

    def perform_create(self, serializer):
        print(self.request.user)
        serializer.save(**self.get_save_kwargs())


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = FunFactComment.objects.all()
    serializer_class = FunFactCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    # methods from other kwargs, add case if  user is diff than author
    def get_queryset(self):
        return super().get_queryset().filter(fact=self.kwargs["fact_id"])

    # def get_object(self):
    #     return super().get_queryset().filter(pk=self.kwargs["pk"])

    def get_save_kwargs(self):
        kwargs = {}
        kwargs["fact"] = self.fact
        kwargs["author"] = self.author
        kwargs["parent"] = self.parent
        kwargs["comment_text"] = self.comment_text
        return kwargs

    def get_serializer_context(self):
        return {"request": self.request}

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

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    # def perform_destroy(self):
    #     # fact = get_object_or_404(FunFact, pk=self.kwargs["fact_id"])
    #     comment = get_object_or_404(FunFactComment, pk=self.kwargs["comment_id"])
    #     return super().perform_destroy(comment)


# TO DO: Fix logic do not use below exception everywhere!
class VoteAlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "You have already voted on this comment"
    default_code = "already_voted"


class VoteNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "There is no vote for this comment"
    default_code = "vote_not_found"


class CommentVotesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, **kwargs):
        comment = get_object_or_404(FunFactComment, pk=kwargs["comment_id"])
        user = self.request.user
        vote_value = kwargs["vote_value"]

        try:
            FunFactVote.objects.create(
                author=user, tagged_object=comment, vote=vote_value
            )
            return response.Response(
                {"message": "successful"}, status=status.HTTP_200_OK
            )
        except IntegrityError:
            raise VoteAlreadyExists

    def delete(self, request, **kwargs):
        comment = get_object_or_404(FunFactComment, pk=kwargs["comment_id"])
        user = self.request.user
        try:
            vote = comment.tags.get(author=user)
        except FunFactVote.DoesNotExist:
            raise VoteNotFound

        vote.delete()
        return response.Response(
            {"message": "record deleted"}, status=status.HTTP_200_OK
        )

    def patch(self, request, **kwargs):
        comment = get_object_or_404(FunFactComment, pk=self.kwargs["comment_id"])
        user = self.request.user
        try:
            vote = comment.tags.get(author=user)
        except FunFactVote.DoesNotExist:
            raise VoteNotFound

        # vote = get_object_or_404(FunFactVote, author=user, tagged_object=comment)
        vote_value = self.kwargs["vote_value"]
        vote.vote = vote_value
        vote.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class FactVotesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, **kwargs):
        fact = get_object_or_404(FunFact, pk=kwargs["fact_id"])
        user = self.request.user
        vote_value = kwargs["vote_value"]

        try:
            print("fact", fact)
            FunFactVote.objects.create(
                author=user, tagged_object=fact, vote=vote_value
            )
            return response.Response(
                {"message": "successful"}, status=status.HTTP_200_OK
            )
        except IntegrityError:
            raise VoteAlreadyExists
        except Exception as e:
            print(e)

    def delete(self, request, **kwargs):
        fact = get_object_or_404(FunFact, pk=kwargs["fact_id"])
        user = self.request.user
        try:
            vote = fact.tags.get(author=user)
        except FunFactVote.DoesNotExist:
            raise VoteNotFound
        vote.delete()
        return response.Response(
            {"message": "record deleted"}, status=status.HTTP_200_OK
        )

    def patch(self, request, **kwargs):
        fact = get_object_or_404(FunFact, pk=kwargs["fact_id"])
        user = self.request.user
        try:
            vote = fact.tags.get(author=user)
        except FunFactVote.DoesNotExist:
            raise VoteNotFound
        vote_value = kwargs["vote_value"]
        vote.vote = vote_value
        vote.save()
        return response.Response(
            {"message": "record updated"}, status=status.HTTP_200_OK
        )
