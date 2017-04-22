from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse

import requests
import re
from io import open as iopen

from imdb_scrapping import get_seasons_info, get_episodes_info

class TVShow(models.Model):
    """
    TV show model:

    """
    title = models.CharField(max_length=100, unique=True)
    info_url = models.CharField(max_length=1000, unique=True)
    poster_url = models.CharField(max_length=1000, unique=True)

    is_next_episode_available = models.BooleanField(default=False)
    next_episode_date = models.DateField(default=None, null=True)

    update_date = models.DateTimeField(default=None)

    def __str__(self):
        """
        Readable str output.
        """
        return self.title

    def update_tvshow(self):
        """
        Update a TV show of the database.
        """
        self.update_date = timezone.now()
        self.save()

    def update_seasons(self):
        """
        Update the seasons list.
        Add the seasons that don't already exist and set their:
            - tvshow
            - number
            - info_url
        """
        seasons_info = get_seasons_info(self)

        for season_info in seasons_info:
            if not self.seasons.filter(number=season_info['season_number']).exists():
                season = Season()
                season.tvshow = self
                season.number = season_info['season_number']
                season.info_url = season_info['season_url']
                season.save()
                self.seasons.add(season)

            else:
                season = self.seasons.get(number=season_info['season_number'])

            # update episode list of each season
            season.update_episodes()

    def get_absolute_url(self):
        """
        Return the TV show page url
        """
        return reverse('Series:tvshow_page', kwargs={'tvshow_pk':self.pk})


class Season(models.Model):
    """
    Season model:

    """
    tvshow = models.ForeignKey(TVShow, related_name='seasons', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    info_url = models.CharField(max_length=1000, unique=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        """
        Readable str output.
        """
        str_output = self.tvshow.title
        str_output += ' Season ' + str(self.number)
        return str_output

    def update_episodes(self):
        """
        Update the episodes list.
        Add the episodes that don't already exist and set their:
            - season
            - number
            - name
        If the episode exists, update the name.
        """
        episodes_info = get_episodes_info(self)

        for episode_info in episodes_info:
            if not self.episodes.filter(number=episode_info['episode_number']).exists():
                episode = Episode()
                episode.season = self
                episode.number = episode_info['episode_number']
                episode.name = episode_info['episode_name']
                episode.save()
                self.episodes.add(episode)

            else:
                episode = self.episodes.get(number=episode_info['episode_number'])
                episode.name = episode_info['episode_name']
                episode.save()

    def all_seen(self):
        """
        Set all episodes to seen
        """
        for episode in self.episodes.all():
            episode.seen = True
            episode.save()


class Episode(models.Model):
    season = models.ForeignKey(Season, related_name='episodes', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=100, default='unknown', null=True)

    seen = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    magnet_link = models.CharField(max_length=1000, default='')

    def __str__(self):
        """
        Readable str output.
        """
        str_output = self.season.tvshow.title
        str_output += ' Season ' + str(self.season.number)
        str_output += ' Episode ' + str(self.number)  
        return str_output

    def get_magnet_link(self):
        pass


def requests_image(file_url, filename):
    """
    Retrieve a image file from a given url and save it at the target location.
    It also returns it's extension.
    """
    suffix_list = ['.jpg', '.gif', '.png', '.tif', '.svg', '.jpeg']
    file_suffix = '.' + file_url.split('.')[-1]
    output_filename = filename + file_suffix
    i = requests.get(file_url)
    if file_suffix in suffix_list and i.status_code == requests.codes.ok:
        with iopen(output_filename, 'wb') as file:
            file.write(i.content)
        return file_suffix
    else:
        return False