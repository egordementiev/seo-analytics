from django.db import models
from django.contrib.auth.models import User


class Site(models.Model):
    ID = models.AutoField(primary_key=True)
    users = models.ManyToManyField(User, related_name='sites')
    domain = models.CharField(max_length=128)
    graphic = models.ImageField()
    graphic_last_update = models.DateTimeField(auto_now_add=True)


class ABTest(models.Model):
    ID = models.AutoField(primary_key=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    url_control_group = models.CharField(max_length=128)
    url_test_group = models.CharField(max_length=128)
    start_date = models.DateField()
    is_finished = models.BooleanField(default=False)
    result = models.FloatField(null=True)
