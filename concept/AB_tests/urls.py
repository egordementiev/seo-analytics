from django.urls import path, include
from .views import *

urlpatterns = [
    path('', hello_world),
    path('add-site-admin/', add_admin_to_site),
    path('delete-site-admin/', delete_admin_from_site),
    path('create-test/', create_ab_test, name='create_ab_test'),
    path('delete-test/', finish_ab_test, name='finish_ab_test'),
    path('create-site/', add_site, name='add_site'),
    path('delete-site/', delete_site, name='delete_site'),
    path('my-sites/', my_sites, name='my_sites'),
]