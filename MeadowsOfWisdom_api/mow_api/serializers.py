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
    username = serializers.CharField(source="author.username", read_only=True)
    user_id = serializers.IntegerField(source="author.id", read_only=True)
    count_votes = serializers.IntegerField(read_only=True)
    user_reaction = serializers.SerializerMethodField()

    def get_user_reaction(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            try:
                return obj.tags.get(author=user).vote
            except FunFactVote.DoesNotExist:
                return None
        return None

    class Meta:
        model = FunFact
        fields = [
            "id",
            "username",
            "user_id",
            "fact_text",
            "count_votes",
            "user_reaction",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "count_votes",
            "upvote",
            "downvote",
            "created_at",
            "updated_at",
        ]


class FunFactCommentSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(source="parent.id", allow_null=True)
    username = serializers.CharField(source="author.username", read_only=True)
    user_id = serializers.IntegerField(source="author.id", read_only=True)
    count_votes = serializers.IntegerField(read_only=True)
    user_reaction = serializers.SerializerMethodField()

    def get_user_reaction(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            try:
                return obj.tags.get(author=user).vote
            except FunFactVote.DoesNotExist:
                return None
        return None

    class Meta:
        model = FunFactComment
        fields = [
            "id",
            "parent_id",
            "username",
            "user_id",
            "count_votes",
            "user_reaction",
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
