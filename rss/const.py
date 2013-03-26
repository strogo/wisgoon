#-*- coding: utf-8 -*-
import string

BAD_WORDS = list(string.punctuation)

BAD_WORDS += [u'از',
             u'به',
             u'شد',
             u'با',
             u'می',
             u'آید',
             u'(ع)',
             u'اگر',
             u'همان',u'چه',u'دارد',u'داری',u'او',u'که',u'،','+','-','.','|',u'؛',u'چرا',u'در',u'است',
             u'می',u'شود',u'را',u'برای',u'حدود',u'اعلام',u'نیست',u'مناسب',u'و',u'برای',u'بار', u'ها']

BAD_WORDS_R = list(string.punctuation)
BAD_WORDS_R += [u'دارم',u'رو',u'،','.','!', u'از',u'ولی',u'میکنند',u'تا',u'است',u'؟',u'های',u'ها',u'؛'
                ]
