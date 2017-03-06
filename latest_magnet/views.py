from django.shortcuts import render, redirect

from .forms import SearchName
from .models import TVShow

def search(request):
    """
    TV show library and search page
    """
    if request.method == 'POST':
        # POST request
        if '_clean' in request.POST:
            # clean the database
            for tvshow in TVShow.objects.all():
                tvshow.delete()
        else:
            form = SearchName(request.POST)
            if form.is_valid():
                title = form['name'].value()
                # if the TV show is not already in the database
                # add it
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

    return render(request, 'latest_magnet/search.html', {'form': form, 'titles': titles})

def tvshow_page(request, title):
    """
    page for a given TV Show.
    """
    tvshow = TVShow.objects.get(title=title)
    return render(request, 'latest_magnet/tvshow_page.html', {'tvshow': tvshow})
