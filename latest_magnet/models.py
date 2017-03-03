from django.db import models

class TVShow(models.Model):
    title = models.CharField(max_length=100)
    current_season = models.PositiveIntegerField()
    current_episode = models.PositiveIntegerField()
    is_next_episode_available = models.BooleanField()
    next_episode_date = models.DateField()