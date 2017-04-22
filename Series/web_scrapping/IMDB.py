"""
TV Show scrapping from www.imdb.com

Functions available:
    - search_tvshow_url
    - get_tvshow_info
    - get_seasons_info
    - get_seasons_info
"""

import requests
import re
from datetime import datetime

def search_tvshow_url(title):
    """
    Find the TV show page on imdb.
    Returns the url containing the information we need on the TV Show.
    """
    search_title = title.lower()
    search_title = search_title.replace(' ', '+')
    search_title = search_title.replace("'", "%27")

    imdb_search_link = 'http://www.imdb.com/find?ref_=nv_sr_fn&q=%s&s=tt' % search_title
    try:
        imdb_search_result = requests.get(imdb_search_link).text
    except requests.exceptions.RequestException:
        raise ValueError("Can't connect to IMDB search page")

    imdb_url_regex = '<tr class="findResult (odd|even)"> '
    imdb_url_regex += '<td class="primary_photo"> '
    imdb_url_regex += '<a href="(?P<imdb_tvshow_url>[^<>]+)" ><img src="[^<>]+" /></a> '
    imdb_url_regex += '</td> <td class="result_text"> '
    imdb_url_regex += '<a href="[^<>]+" >[^<>]+</a>'
    imdb_url_regex += ' \(\d+\) \(TV Series\) </td> </tr>'

    try:
        # retreive the first result
        result = re.finditer(imdb_url_regex, imdb_search_result).next()
    except StopIteration:
        raise ValueError("Can't find IMDB url of tv show %s" % title)
    else:
        # url is a relative url
        imdb_url = 'http://www.imdb.com' + result.groupdict()['imdb_tvshow_url']

    return imdb_url


def get_tvshow_info(tvshow_url):
    """
    Find all the information of a given TV show from IMDB.
    Returns the TV show info:
        - the title
        - the poster url
    """
    try:
        imdb_page = requests.get(tvshow_url).text
    except requests.exceptions.RequestException:
        raise ValueError("Can't connect to IMDB TV show page")

    imdb_img_url_regex = '<img alt="[^<>]+ Poster" title="[^<>]+ Poster"\nsrc="(?P<imdb_tvshow_image>[^<>]+)"\nitemprop="image" />'
    imdb_display_title_regex = '<div class="title_wrapper">\n<h1 itemprop="name" class="">(?P<imdb_display_title>[^<>]+)&nbsp;            </h1>'
    imdb_original_title_regex = '<div class="originalTitle">(?P<imdb_original_title>[^<>]+)<span class="description"> \(original title\)</span></div>'

    # search for original title first
    # if it doesnt exist read the display title
    try:
        result = re.finditer(imdb_original_title_regex, imdb_page).next()
        title = result.groupdict()['imdb_original_title']
    except StopIteration:
        try:
            result = re.finditer(imdb_display_title_regex, imdb_page).next()
            title = result.groupdict()['imdb_display_title']
        except StopIteration:
            raise ValueError("Can't find tv show title on IMDB")

    # get the imdb image url
    try:
        result = re.finditer(imdb_img_url_regex, imdb_page).next()
        poster_url = result.groupdict()['imdb_tvshow_image']
    except StopIteration:
        raise ValueError("Can't find %s tv show IMDB poster" % title)

    return title, poster_url

def get_seasons_info(tvshow):
    """
    Retreive the seasons informations:
        - number
        - page url
    Each season episode info extraction is not performed.
    """
    tvshow_url = re.sub('/\?ref_=(.*)', '', tvshow.info_url)
    episodes_page_url = tvshow_url + '/episodes'

    try:        
        imdb_page = requests.get(episodes_page_url).text
    except requests.exceptions.RequestException:
        raise ValueError("Can't connect to IMDB %s info page" % tvshow.title)

    # regex for scrolling down menu of season
    seasons_menu_regex = '<div class="episode-list-select">\n'
    seasons_menu_regex += '  <div>\n'
    seasons_menu_regex += '    <label for="bySeason">Season:</label>\n'
    seasons_menu_regex += '    <select id="bySeason" tconst="[^<>]+" class="current">\n'
    seasons_menu_regex = '((?:'
    seasons_menu_regex += '      <\!--\n'
    seasons_menu_regex += "      This ensures that we don't wind up accidentally marking two options\n"
    seasons_menu_regex += '      \(Unknown and the blank one\) as selected.\n'
    seasons_menu_regex += '      -->\n'
    seasons_menu_regex += '      <option (?:selected="selected"|) value="\d+">\n'
    seasons_menu_regex += '        \d+\n'
    seasons_menu_regex += '      </option>\n)+?)'
    seasons_menu_regex += '    </select>\n'
    seasons_menu_regex += '  </div>\n'

    # regex of the actual season numbers in this menu
    season_num_regex = '      <option (?:selected="selected"|) value="\d+">\n'
    season_num_regex += '        (?P<season_number>\d+)\n'
    season_num_regex += '      </option>\n'

    try:
        # get the scroll menu
        seasons_menu = re.search(seasons_menu_regex, imdb_page).groups()[0]

        # get the season numbers from this menu
        seasons_info = []
        for season_number_match in re.finditer(season_num_regex, seasons_menu):
            season_info = season_number_match.groupdict()
            season_info['season_url'] = episodes_page_url + '?season=%s' % season_info['season_number']
            seasons_info.append(season_info)
    except:
        raise ValueError("An error occured in the seasons search on IMDB for tvshow %s" % tvshow.title)
    if len(seasons_info) == 0:
        raise ValueError("Can't find any seasons on IMDB for tvshow %s" % tvshow.title)

    return seasons_info

def get_episodes_info(season):
    """
    Retreive the episodes informations:
        - number
        - name
    """
    try:
        imdb_page = requests.get(season.info_url).text
    except requests.exceptions.RequestException:
        raise ValueError("Can't connect to IMDB %s season info page" % season.tvshow.title)

    imdb_episode_regex = '<div class="info" itemprop="episodes" itemscope itemtype="http://schema.org/TVEpisode">\n'
    imdb_episode_regex += '    <meta itemprop="episodeNumber" content="(?P<episode_number>\d+)"/>\n'
    imdb_episode_regex += '    <div class="airdate">\n'
    imdb_episode_regex += '            (?P<episode_airdate>[^<>]+)\n'
    imdb_episode_regex += '    </div>\n'
    imdb_episode_regex += '    <strong><a href="[^<>]+"\ntitle="[^<>]+" itemprop="name">(?P<episode_name>[^<>]+)</a></strong>'

    # get the episodes number and name
    try:
        episodes_info = [episode_info.groupdict() for episode_info in re.finditer(imdb_episode_regex, imdb_page)]
    except:
        raise ValueError("An error occured in the episodes search on IMDB for season %s of %s" % (season.number, season.tvshow.title))
    if len(episodes_info) == 0:
        raise ValueError("Can't find any episodes on IMDB for season %s of %s" % (season.number, season.tvshow.title))

    for episode_info in episodes_info:
        if len(episode_info['episode_airdate']) == 4:
            # year only
            episode_info['episode_airdate'] = None
        else:
            # full date :
            # remove dot and convert it to a proper datetime object
            airdate = episode_info['episode_airdate'].replace('.', '')
            episode_info['episode_airdate'] = datetime.strptime(airdate, '%d %b %Y')

        if episode_info['episode_name'].startswith("Episode #"):
            # unknown name of episode yet
            episode_info['episode_name'] = None

    return episodes_info
