from rss.const import BAD_WORDS


def clean_words(string):
    for w in BAD_WORDS:
        string = string.replace(" "+ w+ " ", ' ')
    return string
    