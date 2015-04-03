#-*- coding:utf-8 -*-
_farsi_unicode_norm = {
    u'\u064a': u'\u06cc',  # yeh
    u'\u0649': u'\u06cc',  # yeh
    u'\u0643': u'\u06a9',  # keh
}


def normalize_tags(t):
    text = list(t)
    lt = len(text)
    for i in range(lt):
        c = text[i]

        text[i] = _farsi_unicode_norm.get(c, c)
    t = u''.join(text)
    return t
