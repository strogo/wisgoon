from pin.api6 import urls
from pin.api6.http import return_json_data
from operator import itemgetter


def get_urls(raw_urls, nice_urls=[], urlbase=''):
    for entry in raw_urls:
        fullurl = (urlbase + entry.regex.pattern).replace('^', '')
        if entry.callback:
            a = entry.regex.pattern.split('/')[0]
            if fullurl.startswith(a):
                viewname = entry.callback.func_name
                nice_urls.append({"pattern": fullurl, "location": viewname})
        else:
            get_urls(entry.url_patterns, nice_urls, fullurl)
    nice_urls = sorted(nice_urls, key=itemgetter('pattern'))
    return nice_urls


def show_map(request):
    a = {}
    a['urls'] = get_urls(urls.urlpatterns)

    return return_json_data(a)
