from django.contrib.auth.models import Group, User
from mow_api.models import FunFact, FunFactComment, FunFactVote
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )

    class Meta:
        model = User
        fields = ["id", "username", "password"]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class FunFactSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="author.username")

    class Meta:
        model = FunFact
        fields = [
            "id",
            "username",
            "fact_text",
            "upvote",
            "downvote",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "username",
            "upvote",
            "downvote",
            "created_at",
            "updated_at",
        ]


class FunFactCommentSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(source="parent.id", allow_null=True)
    username = serializers.CharField(source="author.username", read_only=True)
    count_votes = serializers.IntegerField(read_only=True)
    # field to use on  store output of method from models which returns all votes
    # all_votes = serializers.ReadOnlyField(source="get_votes")

    class Meta:
        model = FunFactComment
        fields = [
            "id",
            "parent_id",
            "username",
            "count_votes",
            "all_votes",
            "comment_text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class VoteRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, FunFact):
            serializer = FunFactSerializer(value)
        elif isinstance(value, FunFactComment):
            serializer = FunFactCommentSerializer(value)
        else:
            raise Exception("Unexpected type of tagged object")
        return serializer.data


class FunFactVoteSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="author.username", read_only=True)
    vote_target = VoteRelatedField(read_only=True)

    class Meta:
        model = FunFactVote
        fields = [
            "id",
            "username",
            "vote_target",
            "vote",
        ]
        read_only_fields = [
            "id",
        ]
