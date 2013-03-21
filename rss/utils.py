from rss.const import BAD_WORDS
import tldextract

def clean_words(string):
    for w in BAD_WORDS:
        string = string.replace(" "+ w+ " ", ' ')
    return string
 
def get_host(url):
    tld = tldextract.extract(url)
    host = ""
    if tld.domain and tld.tld:
        host = tld.domain + "_" + tld.tld
        return host

    return None
