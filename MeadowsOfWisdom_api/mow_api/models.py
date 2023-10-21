from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey


class TimeTrackedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Reaction(models.Model):
    upvote = models.PositiveIntegerField(default=0)
    downvote = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


class FunFactVote(models.Model):
    author = models.ForeignKey(
        User, related_name="votes_author", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    tagged_object = GenericForeignKey("content_type", "object_id")

    class VoteType(models.TextChoices):
        UPVOTE = "upvote"
        DOWNVOTE = "downvote"

    vote = models.CharField(max_length=10, choices=VoteType.choices)

    class Meta:
        unique_together = ["author", "content_type", "object_id"]

    def __str__(self) -> str:
        return self.vote


class FunFact(TimeTrackedModel, Reaction):
    author = models.ForeignKey(User, related_name="facts", on_delete=models.CASCADE)
    fact_text = models.TextField()
    tags = GenericRelation(FunFactVote)

    class Meta:
        verbose_name = "Fun Fact"
        verbose_name_plural = "Fun Facts"

    def __repr__(self) -> str:
        return f"<FunFact author= {self.author.username} fact_text= {self.fact_text} date= {self.date} >"

    def __str__(self):
        return self.fact_text


class FunFactComment(TimeTrackedModel):
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    fact = models.ForeignKey(FunFact, related_name="comments", on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", related_name="replies", on_delete=models.CASCADE, null=True, blank=True
    )
    comment_text = models.TextField()
    tags = GenericRelation(FunFactVote)

    def count_votes(self):
        upvote_count = self.votes_fact.filter(vote="upvote").count()
        downvote_count = self.votes_fact.filter(vote="downvote").count()
        return upvote_count - downvote_count

    # @property
    # def get_votes(self):
    #     return self.votes_fact.all()

    def __str__(self) -> str:
        return self.comment_text
