# -*- coding:utf-8 -*-
def normalize(text):
    replace_dict = {
        u'۰': '0',
        u'۱': '1',
        u'۲': '2',
        u'۳': '3',
        u'۴': '4',
        u'۵': '5',
        u'۶': '6',
        u'۷': '7',
        u'۸': '8',
        u'۹': '9',
        u'.': '.',
        u'\u06f0': '0',
        u'\u06f1': '1',
        u'\u06f2': '2',
        u'\u06f3': '3',
        u'\u06f4': '4',
        u'\u06f5': '5',
        u'\u06f6': '6',
        u'\u06f7': '7',
        u'\u06f8': '8',
        u'\u06f9': '9',
        u'\u002e': '.',
        u'\u0668': '8',
    }
    for r in replace_dict:
        text = text.replace(r, replace_dict[r])
    return text
