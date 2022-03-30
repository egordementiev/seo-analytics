from django.db import models


class ABTest(models.Model):
    ID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)
    description = models.TextField()
    start_group_a_date = models.DateTimeField()
    start_group_b_date = models.DateTimeField()
    is_finished = models.BooleanField(default=False)


class Site(models.Model):
    ID = models.AutoField(primary_key=True)
    url = models.CharField(max_length=32)
    user = models.ForeignKey()


class Result(models.Model):
    ID = models.AutoField(primary_key=True)
    percent = models.FloatField()
    mark = models.IntegerField()


class User(models.Model):
    ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=64)
    login = models.CharField(max_length=32)
    password = models.CharField(max_length=128)


# Create your models here.
