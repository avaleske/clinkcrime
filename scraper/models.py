from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Event(models.Model):
    trumba_id = models.IntegerField()
    datetime = models.DateTimeField()
    title = models.CharField(max_length=100)
    location = models.TextField(max_length=100)
