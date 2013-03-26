from django.core.cache import cache
from rss.const import BAD_WORDS, BAD_WORDS_R
import tldextract

def word_limit(string, limit=20):
    words = string.split()
    return ' '.join(words[:limit])

def clean_words(string):
    string = word_limit(string, limit=15)

    for w in BAD_WORDS:
        string = string.replace(" "+ w+ " ", ' ')

    for wp in BAD_WORDS_R:
        string = string.replace(wp,'')

    return string

def get_host(url):
    tld = cache.get('host'+url)
    if not tld:
        tld = tldextract.extract(url)
        cache.set('host'+url, tld, 300)
    
    host = ""
    if tld.domain and tld.tld:
        host = tld.domain + "_" + tld.tld
        return (tld.domain, tld.tld)

    return None
