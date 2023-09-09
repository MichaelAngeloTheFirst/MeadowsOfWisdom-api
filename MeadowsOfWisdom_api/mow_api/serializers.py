from django.contrib.auth.models import User, Group
from rest_framework import serializers
from mow_api.models import FunFact




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

    class Meta:
        model = FunFact
        fields = ["id", "fact_text", "upvote",
                  "downvote", "created_at", "updated_at"]
        read_only_fields = ["id", "upvote",
                            "downvote",  "created_at", "updated_at"]
