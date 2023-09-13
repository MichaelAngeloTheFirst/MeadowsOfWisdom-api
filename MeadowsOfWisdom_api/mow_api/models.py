from django.contrib.auth.models import User
from django.db import models


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


class FunFactComment(TimeTrackedModel, Reaction):
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    fact = models.ForeignKey(FunFact, related_name="comments", on_delete=models.CASCADE)
    comment_text = models.TextField()

    def __str__(self) -> str:
        return self.comment_text
