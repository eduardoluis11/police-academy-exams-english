from django.db import models

# This will let me import the AbstractUser model to be able to authenticate my users
from django.contrib.auth.models import AbstractUser

# Create your models here.

""" AbstractUser model, which is a model that will let me authenticate my users.
"""


class User(AbstractUser):
    pass
