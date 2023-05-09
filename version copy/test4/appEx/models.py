from django.db import models
from django import forms

# Create your models here.
class Acc(models.Model):
    username=models.CharField(max_length=30)
    password=models.CharField(max_length=1000)
    balance=models.FloatField()
    created=models.CharField(max_length=20, default="")
class Invested(models.Model):
    name=models.CharField(max_length=30)
    invested=models.CharField(max_length=30)
    price=models.FloatField(default=0.0)
    shares=models.FloatField(default=0.0)

class FavoriteStock(models.Model):
    name=models.CharField(max_length=30)
    favorite=models.CharField(max_length=30)
class Message(models.Model):
    sender=models.CharField(max_length=30)
    receive=models.CharField(max_length=30)
    content=models.CharField(max_length=1000)