from django.db import models
from django.utils import timezone

class TVShow(models.Model):
    """
    TV show model:

    """
    title = models.CharField(max_length=100, unique=True)
    url = models.CharField(max_length=100, unique=True)
    current_season = models.PositiveIntegerField()
    last_seen_episode = models.PositiveIntegerField()
    is_next_episode_available = models.BooleanField()
    update_date = models.DateTimeField(default=None)
    next_episode_date = models.DateField(default=None, null=True)

    def add_new(self, title):
        """
        add a new TV show to the database.
        """
        self.title = title.lower() # title must be only lower case
        self.url = title_to_url(title)
        self.current_season = 1
        self.last_seen_episode = 1
        self.is_next_episode_available = True
        self.update_date = timezone.now()
        self.save()

def title_to_url(title):
    url = title.replace(' ', '.') # replace spaces by dots
    url = url.replace("'", "") # remove '
    url = url.lower() # make sure it is only lower case
    return url