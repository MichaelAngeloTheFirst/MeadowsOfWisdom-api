from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, Count, F


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


class FunFact(TimeTrackedModel, Reaction):
    author = models.ForeignKey(User, related_name="facts", on_delete=models.CASCADE)
    fact_text = models.TextField()

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

    def count_votes(self):
        upvote_count = self.votes_fact.filter(vote="upvote").count()
        downvote_count = self.votes_fact.filter(vote="downvote").count()
        return upvote_count - downvote_count

    def __str__(self) -> str:
        return self.comment_text


class FunFactVote(models.Model):
    author = models.ForeignKey(
        User, related_name="votes_author", on_delete=models.CASCADE
    )
    fact_comment = models.ForeignKey(
        FunFactComment, related_name="votes_fact", on_delete=models.CASCADE
    )

    class VoteType(models.TextChoices):
        UPVOTE = "upvote"
        DOWNVOTE = "downvote"

    vote = models.CharField(max_length=10, choices=VoteType.choices)

    class Meta:
        unique_together = ["author", "fact_comment"]

    def __str__(self) -> str:
        return self.vote
