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
                return redirect('/latest_magnet/tvshow_%s_page' % tvshow.url)

    else:
        form = SearchName()

    # create the library
    titles = []
    for tvshow in TVShow.objects.order_by('-update_date'):
        titles.append(tvshow.title)

    return render(request, 'latest_magnet/library.html', {'form': form, 'titles': titles})

def tvshow_page(request, title):
    """
    page for a given TV Show.
    """
    tvshow = TVShow.objects.get(title=title)
    if request.method == 'POST':
        if '_to_library' in request.POST:
            # redirect to library page
            return redirect('/latest_magnet')
    return render(request, 'latest_magnet/tvshow_page.html', {'tvshow': tvshow})
