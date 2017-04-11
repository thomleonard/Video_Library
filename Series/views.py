from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from datetime import timedelta

from .models import TVShow, Episode

from web_scrapping.IMDB import search_tvshow_url


def library(request):
    """
    TV show library page
    """
    # get the TV shows by their last watched order
    update_ordered_tvshows = TVShow.objects.order_by('-last_watched')

    template = 'Series/library.html'
    context = {'tvshows': update_ordered_tvshows}
    return render(request, template, context)


def search(request):
    """
    TV show search page
    """
    title = request.GET['search_input']

    try:
        # get TV show infos
        tvshow_url = search_tvshow_url(title)

        # if the TV show is not already in the database
        # add it otherwise get the existing one
        if not TVShow.objects.filter(info_url=tvshow_url).exists():
            tvshow = TVShow()
            tvshow.info_url = tvshow_url
            # update tv show information and save it
            tvshow.update_info() 
        else:
            tvshow = TVShow.objects.get(info_url=tvshow_url)
    except ValueError as error:
        # error in the web scrapping proccess
        template = 'Series/base.html'
        context = {'error_message': str(error)}
        return render(request, template, context)
    else:
        return redirect(tvshow)


def empty_library(request):
    """
    View to empty the TV show database.
    """
    TVShow.objects.all().delete()
    return redirect('Series:library')


def tvshow_page(request, tvshow_pk):
    """
    View for a given TV Show.
    """
    # get the tvshow object if it exists, raise 404 error otherwise
    tvshow = get_object_or_404(TVShow, pk=tvshow_pk)

    # update the last watched field every time the tv show is accessed
    tvshow.last_watched = timezone.now()
    tvshow.save()

    # check if the update date is more than 24hours
    if (timezone.now() - tvshow.update_date) > timedelta(hours=24):
        tvshow.update_info()

    template = 'Series/tvshow_page.html'
    context = {'tvshow': tvshow}
    return render(request, template, context)


def episode_seen(request, episode_pk):
    """
    View to change the seen status of an episode.
    """
    # get the episode object if it exists, raise 404 error otherwise
    episode = get_object_or_404(Episode, pk=episode_pk)
    
    # if we set an episode to seen, we set all the previous one too
    season = episode.season
    if not episode.seen:
        # in the same season
        for previous_episode in season.episodes.filter(number__lt=episode.number):
            previous_episode.seen = True
            previous_episode.save()
        # in previous season
        for previous_season in season.tvshow.seasons.filter(number__lt=season.number):
            previous_season.all_seen()

    # change the value of the episode
    episode.seen = not episode.seen
    episode.save()

    # has to refresh the active season field
    season.tvshow.set_active_season()

    return redirect(episode.season.tvshow)


def upcoming(request):
    """
    View to show the upcoming TV show episodes.
    """
    # get all the episodes which airdate is today or after
    upcoming_episodes = Episode.objects.filter(airdate__gte=timezone.now()).order_by('airdate')
    grouped_episodes = []
    if len(upcoming_episodes) > 0:
        grouped_episodes.append([upcoming_episodes[0], ])
        for episode in upcoming_episodes[1:]:
            if episode.airdate == grouped_episodes[-1][0].airdate:
                grouped_episodes[-1].append(episode)
            else:
                grouped_episodes.append([episode, ])

    template = 'Series/upcoming.html'
    context = {'upcoming_episodes': grouped_episodes}
    return render(request, template, context)


def episode_magnet(request, episode_pk):
    """
    View to search for an episode magnet link.
    """
    # get the episode object if it exists, raise 404 error otherwise
    episode = get_object_or_404(Episode, pk=episode_pk)
    episode.get_magnets()


    #return redirect(episode.season.tvshow)
    template = 'Series/tvshow_page.html'
    context = {'tvshow': episode.season.tvshow,
               'dropdown_episode': episode.pk}
    return render(request, template, context)

