from django.shortcuts import render

from .forms import SearchName
from .models import TVShow

def search(request):
    """
    TV Show search page
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
        pass
    form = SearchName()

    print 'len', len(TVShow.objects.all())
    # print 'get', TVShow.objects.get(title='yo')

    # instance = SomeModel.objects.get(id=id)
    # instance.delete()
    for tvshow in TVShow.objects.order_by('-update_date'):
        print tvshow.update_date, tvshow.title
    return render(request, 'latest_magnet/search.html', {'form': form})