from django.shortcuts import render, redirect, get_object_or_404

from .forms import SearchName
from .models import TVShow


def library(request):
    """
    TV show library and search page
    """
    if request.method == 'POST':
        form = SearchName(request.POST)
        if form.is_valid():
            title = form['name'].value()
            title = title.lower() # convert to lower case
            # if the TV show is not already in the database
            # add it otherwise get the existing one
            if not TVShow.objects.filter(title=title).exists():
                tvshow = TVShow()
                try:
                    tvshow.add_new(title)
                except ValueError as error:
                    # error in the web scrapping proccess
                    template = 'Series/library.html'
                    context = {'form': SearchName(), 
                               'error_message': str(error)}
                    return render(request, template, context)
            else:
                tvshow = TVShow.objects.get(title=title)
            return redirect(tvshow)

    # create the library
    update_ordered_tvshows = TVShow.objects.order_by('-update_date')

    template = 'Series/library.html'
    context = {'form': SearchName(), 
               'tvshows': update_ordered_tvshows}
    return render(request, template, context)


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

    # everytime a tv show is accessed we update it
    tvshow.update_tvshow()

    template = 'Series/tvshow_page.html'
    context = {'tvshow': tvshow}
    return render(request, template, context)
