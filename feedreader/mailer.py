# -*- encoding: utf-8 -*-

import smtplib
import sys
import os
from django.contrib.auth.models import User

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

from django.core.management import setup_environ 
import settings
setup_environ(settings)

from django.template.loader import render_to_string

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import lxml.html
import re

from pin.models import Notify

def stripIt(s):
    doc = lxml.html.fromstring(s)   # parse html string
    txt = doc.xpath('text()')       # ['foo ', ' bar']
    txt = ' '.join(txt)             # 'foo   bar'
    return re.sub('\s+', ' ', txt)  # 'foo bar'

me = "mailer@wisgoon.com"
you = "vchakoshy@gmail.com"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Link"
msg['From'] = me
msg['To'] = you

# Create the body of the message (a plain-text and an HTML version).
#email_content = get_template('mailer/mail.html')
users = User.objects.all()
for user in users:
    notify = Notify.objects.all().filter(user_id=user.id, seen=0)

    email_content = render_to_string('mailer/notify.html',{'notify':notify})
    #email_content = open('templates/mailer/mail.html', 'r').read()
    #f = open('out.html','w+')
    #f.write(email_content.encode('utf-8'))
    #f.close()
    
    text = stripIt(email_content)
    html = email_content
    
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain', _charset='utf-8')
    part2 = MIMEText(html, 'html', _charset='utf-8')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()