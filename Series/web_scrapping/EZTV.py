"""
Magnet scrapping from eztv.bypassed.cool

Functions available:
    - get_episode_magnet
"""

import requests
import re

def get_episode_magnet(episode):
    """
    Find the episode eztv.
    Returns the magnet link corresponding.
    """
    title = episode.season.tvshow.title
    search_title = title.lower()
    search_title.replace(' ', '-')
    search_title.replace("'", '')
    search_title += '-S%02dE%02d' % (episode.season.number, episode.number)

    eztv_search_link = 'https://eztv.bypassed.cool/search/' + search_title

    try:
        search_result = requests.get(eztv_search_link).text
    except requests.exceptions.RequestException:
        raise ValueError("Can't connect to EZTV search page")

    eztv_magnet_regex = '<tr name="hover" class="forum_header_border">\n'
    eztv_magnet_regex += '<td width="\d+" class="forum_thread_post" align="center"><a href="[^<>]+" title="[^<>]+"><img src="[^<>]+" border="0" alt="Info" title="[^<>]+"></a></td>\n'
    eztv_magnet_regex += '<td class="forum_thread_post">\n'
    eztv_magnet_regex += '<a href="[^<>]+" title="[^<>]+" alt="[^<>]+" class="epinfo">(?P<file_name>[^<>]+)</a>\n'
    eztv_magnet_regex += '</td>\n'
    eztv_magnet_regex += '<td align="center" class="forum_thread_post">\n'
    eztv_magnet_regex += '<a href="(?P<magnet_link>[^<>]+)" class="magnet" title="[^<>]+" rel="nofollow"></a>\n'
    eztv_magnet_regex += '(|<a href="[^<>]+" rel="nofollow" class="download_1" title="[^<>]+"></a>\n)' # this is not always available
    eztv_magnet_regex += '</td>\n'
    eztv_magnet_regex += '<td align="center" class="forum_thread_post">(?P<file_size>[^<>]+)</td>\n'
    eztv_magnet_regex += '<td align="center" class="forum_thread_post">[^<>]+</td>\n'
    eztv_magnet_regex += '<td align="center" class="forum_thread_post"><font color="[^<>]+">(?P<seeds_number>[^<>]+)</font></td>\n'
    eztv_magnet_regex += '<td align="center" class="forum_thread_post_end">'

    # get the episodes number and name
    try:
        magnets = [magnet_info.groupdict() for magnet_info in re.finditer(eztv_magnet_regex, search_result)]
    except:
        raise ValueError("An error occured in the magnet search on EZTV for %s Season %s Episode %s" % (episode.season.tvshow.title, episode.season.number, episode.number))

    if not magnets:
        raise ValueError("Couldn't find any magnet on EZTV for %s Season %s Episode %s" % (episode.season.tvshow.title, episode.season.number, episode.number))

    return magnets