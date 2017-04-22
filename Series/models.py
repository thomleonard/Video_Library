from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse

import requests
import re
from io import open as iopen

from web_scrapping.IMDB import get_tvshow_info, get_seasons_info, get_episodes_info
from web_scrapping.EZTV import get_episode_magnet


class TVShow(models.Model):
    """
    TV show model:
        - title
        - info_url is the URL where the information needed on the TV show
        (title, poster, seasons) can be scrapped
        - poster_url is the URL of the poster image

        - active_season
        - is_next_episode_available
        - next_episode_date

        - last_watched is the last time the user went on the TV show page
        - update_date is the last time the information have been retreived
    """
    title = models.CharField(max_length=100, unique=True)
    info_url = models.CharField(max_length=1000, unique=True)
    poster_url = models.CharField(max_length=1000, unique=True)

    active_season = models.PositiveIntegerField(default=1)
    is_next_episode_available = models.BooleanField(default=False)

    update_date = models.DateTimeField(default=None)
    last_watched = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        Readable str output.
        """
        return self.title

    def update_info(self):
        """
        Update a TV show of the database.
        """
        title, poster_url = get_tvshow_info(self.info_url)
        self.title = title
        self.poster_url = poster_url
        self.update_date = timezone.now()
        self.save()
        self.update_seasons()
        self.set_active_season()

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

    def set_active_season(self):
        for season in self.seasons.all():
            for episode in season.episodes.all():
                if not episode.seen:
                    self.active_season = season.number
                    self.save()
                    return
        # if it hasn't been set, set it to the last season
        self.active_season = season.number
        self.save()

    def get_absolute_url(self):
        """
        Return the TV show page url
        """
        return reverse('Series:tvshow_page', kwargs={'tvshow_pk':self.pk})


class Season(models.Model):
    """
    Season model:
        - tvshow
        - number
        - info_url is the URL where the seasons episodes information can be scrapped
    """
    tvshow = models.ForeignKey(TVShow, related_name='seasons', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    info_url = models.CharField(max_length=1000, unique=True)

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
                if episode_info['episode_name']:
                    episode.name = episode_info['episode_name']
                if episode_info['episode_airdate']:
                    episode.airdate = episode_info['episode_airdate']
                episode.save()
                self.episodes.add(episode)

            else:
                episode = self.episodes.get(number=episode_info['episode_number'])
                if episode_info['episode_name']:
                    episode.name = episode_info['episode_name']
                if episode_info['episode_airdate']:
                    episode.airdate = episode_info['episode_airdate']
                episode.save()

    def all_seen(self):
        """
        Set all episodes to seen
        """
        for episode in self.episodes.all():
            episode.seen = True
            episode.save()


class Episode(models.Model):
    """
    Season model:
        - season
        - number
        - name
        - airdate

        - seen
        - available
        - magnet_link
    """

    season = models.ForeignKey(Season, related_name='episodes', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=100, default='unknown', null=True)
    airdate = models.DateField(default=None, null=True)

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

    def get_magnets(self):
        magnets_info = get_episode_magnet(self)

        for magnet_info in magnets_info:
            if not self.magnets.filter(link=magnet_info['magnet_link']).exists():
                magnet = Magnet()
                magnet.episode = self
                magnet.link = magnet_info['magnet_link']
                magnet.file_name = magnet_info['file_name']
                magnet.file_size = magnet_info['file_size']
                magnet.seeds_number = magnet_info['seeds_number']
    
                magnet.save()
                self.magnets.add(magnet)
            else:
                magnet = self.magnets.get(link=magnet_info['magnet_link'])
                magnet.seeds_number = magnet_info['seeds_number']
                magnet.save()


class Magnet(models.Model):
    """
    Magnet model:
        - episode
        - link
        - file_name
        - file_size
        - seeds_number
    """

    episode = models.ForeignKey(Episode, related_name='magnets', on_delete=models.CASCADE)
    link = models.CharField(max_length=1000, default='', unique=True)
    file_name = models.CharField(max_length=100, default='')
    file_size = models.CharField(max_length=100, default='unknown')
    seeds_number = models.PositiveIntegerField()

    def __str__(self):
        """
        Readable str output.
        """
        str_output = self.episode.season.tvshow.title
        str_output += ' Season ' + str(self.episode.season.number)
        str_output += ' Episode ' + str(self.episode.number)  
        return str_output


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
