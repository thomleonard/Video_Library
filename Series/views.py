from django.http import Http404
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
            TVShow.objects.all().delete()
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

    template = 'Series/library.html'
    context = {'form': form, 
               'tvshows': update_ordered_tvshows}
    return render(request, template, context)


def tvshow_page(request, tvshow_pk):
    """
    Page for a given TV Show.
    """
    # get the tvshow object if it exists, raise 404 error otherwise
    try:
        tvshow = TVShow.objects.get(pk=tvshow_pk)
    except:
        raise Http404('TV show is not in your library')

    # everytime a tv show is accessed we update it
    tvshow.update_tvshow()

    if request.method == 'POST':
        if '_to_library' in request.POST:
            # redirect to library page
            return redirect('/Series')

    template = 'Series/tvshow_page.html'
    context = {'tvshow': tvshow}
    return render(request, template, context)
