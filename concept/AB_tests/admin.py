from django.contrib import admin
from .models import Site, ABTest

admin.site.register(Site)
admin.site.register(ABTest)

# Register your models here.
