from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class SpeechData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=256)
    chapter = models.CharField(max_length=256)
    text = models.TextField()
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.subject} - {self.chapter} - {self.date_recorded}'
    

class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=256)
    chapter = models.CharField(max_length=256)
    notes = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class Quiz(models.Model):
    subject = models.CharField(max_length=256)
    chapter = models.CharField(max_length=256)
    question_text = models.TextField()
    answer_choices = models.TextField()
    correct_answer = models.TextField()

class QuizScorecard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=256)
    chapter = models.CharField(max_length=256)
    score = models.IntegerField()
    date_recorded = models.DateTimeField(auto_now_add=True)