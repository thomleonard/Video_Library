from django.shortcuts import render

from .forms import SearchName


def search(request):
    """
    TV Show search page
    """
    if request.method == 'POST':
        # POST request
        form = SearchName(request.POST)
        if form.is_valid():
            print 'valid form'
            tvshow_title = form['name'].value()
            print tvshow_title
            #return redirect('/latest_magnet/' + forecast_date)
    else: # GET
        form = SearchName()
    return render(request, 'latest_magnet/search.html', {'form': form})