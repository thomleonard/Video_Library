from django.shortcuts import render, redirect

from .forms import SearchName
from .models import TVShow

def library(request):
    """
    TV show library and search page
    """
    if request.method == 'POST':
        if '_clean' in request.POST:
            # clean the database
            for tvshow in TVShow.objects.all():
                tvshow.delete()
        else:
            form = SearchName(request.POST)
            if form.is_valid():
                title = form['name'].value()
                title = title.lower() # convert to lower case
                # if the TV show is not already in the database
                # add it otherwise get the existing one
                if not TVShow.objects.filter(title=title).exists():
                    tvshow = TVShow()
                    tvshow.add_new(title)
                else:
                    tvshow = TVShow.objects.get(title=title)
                return redirect('/Series/tvshow_%s_page' % tvshow.url)

    form = SearchName()

    # create the library
    update_ordered_tvshows = TVShow.objects.order_by('-update_date')
    is_library_empty = len(update_ordered_tvshows) > 0

    return render(request, 'Series/library.html', 
        {'form': form, 
         'tvshows': update_ordered_tvshows,
         'is_library_empty': is_library_empty})

def tvshow_page(request, title_url):
    """
    page for a given TV Show.
    """
    tvshow = TVShow.objects.get(url=title_url)
    # everytime a tv show is accessed we update it
    tvshow.update_tvshow()

    if request.method == 'POST':
        if '_to_library' in request.POST:
            # redirect to library page
            return redirect('/Series')

    return render(request, 'Series/tvshow_page.html', {'tvshow': tvshow})
