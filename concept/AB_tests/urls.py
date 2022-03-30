from django.urls import path, include
from .views import hello_world
from .views import create_ab_test, finish_ab_test

urlpatterns = [
    path('', hello_world),
    path('create/', create_ab_test, name='create_ab_test'),
    path('finish/', finish_ab_test, name='finish_ab_test'),
]