"""
TV Show scrapping from www.imdb.com
"""
import requests
import re


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
        raise ValueError("Can't connect to www.imdb.com")

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
        imdb_url = 'http://www.imdb.com' + result.groupdict()['imdb_tvshow_url']
    return imdb_url


def get_tvshow_info(tvshow_url):
    """
    Find all the information of a given TV show from IMDB.
    Return :
        - the diplay title
        - the poster url
    """
    imdb_page = requests.get(tvshow_url).text

    imdb_img_url_regex = '<img alt="[^<>]+ Poster" title="[^<>]+ Poster"\nsrc="(?P<imdb_tvshow_image>[^<>]+)"\nitemprop="image" />'
    imdb_display_title_regex = '<div class="title_wrapper">\n<h1 itemprop="name" class="">(?P<imdb_display_title>[^<>]+)&nbsp;            </h1>'
    imdb_original_title_regex = '<div class="originalTitle">(?P<imdb_original_title>[^<>]+)<span class="description"> \(original title\)</span></div>'
    
    # search for original title first
    # if it doesnt exist read the display title
    try:
        result = re.finditer(imdb_original_title_regex, imdb_page).next()
        display_title = result.groupdict()['imdb_original_title']
    except StopIteration:
        try:
            result = re.finditer(imdb_display_title_regex, imdb_page).next()
            display_title = result.groupdict()['imdb_display_title']
        except StopIteration:
            raise ValueError("Can't find tv show IMDB display title")

    # get the imdb image
    try:
        result = re.finditer(imdb_img_url_regex, imdb_page).next()
        poster_url = result.groupdict()['imdb_tvshow_image']
    except StopIteration:
        raise ValueError("Can't find tv show IMDB poster")

    return display_title, poster_url