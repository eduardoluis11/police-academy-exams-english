from django.contrib import admin

# Register your models here.
from .models import User

# This will show my registered users in my django admin panel
admin.site.register(User)
