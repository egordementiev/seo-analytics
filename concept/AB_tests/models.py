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
    urls_control_group = models.TextField()
    urls_test_group = models.TextField()
    start_date = models.DateField()
    is_finished = models.BooleanField(default=False)
    result = models.FloatField(null=True)

    def get_urls_control_group(self) -> list:
        return self.urls_control_group.split('\r\n')

    def set_urls_control_group(self, list_of_urls: list):
        self.urls_control_group = '\r\n'.join(list_of_urls)
        print(f'new urls_control_group is {self.urls_control_group}  |')

    def get_urls_test_group(self) -> list:
        return self.urls_test_group.split('\r\n')

    def set_urls_test_group(self, list_of_urls: list):
        self.urls_test_group = '\r\n'.join(list_of_urls)
        print(f'new urls_test_group is {self.urls_test_group}  |')
