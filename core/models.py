from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ModelBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Topic(ModelBase):
    name = models.CharField(max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name='topics')


class Location(ModelBase):
    name = models.CharField(max_length=200, unique=True)
    woeid = models.IntegerField()
    # users = models.ManyToManyField(User, related_name='locations')
