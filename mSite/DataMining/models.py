from django.db import models
from django.contrib.auth.models import User

class userPreferences(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    logoutTimeout =  models.IntegerField()
    bgColor = models.CharField(max_length=6)
    
    class Meta:
        db_table = 'datamining_userpreferences'