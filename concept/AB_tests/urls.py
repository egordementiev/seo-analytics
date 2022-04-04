from django.urls import path, include
from .views import hello_world
from .views import create_ab_test, finish_ab_test, add_site, add_admin_to_site

urlpatterns = [
    path('', hello_world),
    path('add_admin_to_site', add_admin_to_site),
    path('create/', create_ab_test, name='create_ab_test'),
    path('finish/', finish_ab_test, name='finish_ab_test'),
    path('add_site/', add_site, name='add_site')
]