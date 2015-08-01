from django.core.urlresolvers import reverse

from pin.api_tools import abs_url


def get_next_url(url_name, offset=None, token=None, url_args={}, **kwargs):
    n_url_p = reverse(url_name, kwargs=url_args) + "?"
    if offset:
        n_url_p = n_url_p + "offset=%s" % (offset)
    if token:
        n_url_p = n_url_p + "&token=%s" % (token)
    for k, v in kwargs.iteritems():
        n_url_p = n_url_p + "&%s=%s" % (k, v)
    return abs_url(n_url_p)
