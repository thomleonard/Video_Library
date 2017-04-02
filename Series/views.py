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
                return redirect('/Series/tvshow_%s' % tvshow.pk)

    form = SearchName()

    # create the library
    update_ordered_tvshows = TVShow.objects.order_by('-update_date')
    is_library_empty = len(update_ordered_tvshows) == 0

    template = 'Series/library.html'
    context = {'form': form, 
        'tvshows': update_ordered_tvshows,
        'is_library_empty': is_library_empty}
    return render(request, template, context)


def tvshow_page(request, tvshow_pk):
    """
    page for a given TV Show.
    """
    tvshow = TVShow.objects.get(pk=tvshow_pk)
    # everytime a tv show is accessed we update it
    tvshow.update_tvshow()

    if request.method == 'POST':
        if '_to_library' in request.POST:
            # redirect to library page
            return redirect('/Series')

    template = 'Series/tvshow_page.html'
    context = {'tvshow': tvshow}
    return render(request, template, context)
