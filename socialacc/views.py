# Create your views here.

from django.contrib.auth.models import User
from django.http import get_host
from django.shortcuts import render_to_response as render
from django.utils.html import escape
import gdata.contacts.service

GOOGLE_CONTACTS_URI = 'http://www.google.com/m8/feeds/'

def get_url_host(request):
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    host = escape(get_host(request))
    return '%s://%s' % (protocol, host)

def get_full_url(request):
    return get_url_host(request) + request.get_full_path()

def get_auth_sub_url(next):
    scope = GOOGLE_CONTACTS_URI
    secure = False
    session = True
    contacts_service = gdata.contacts.service.ContactsService()
    return contacts_service.GenerateAuthSubURL(next, scope, secure, session);

def get_contact_emails(authsub_token):
    contacts_service = gdata.contacts.service.ContactsService()
    contacts_service.auth_token = authsub_token
    contacts_service.UpgradeToSessionToken()
    emails = []
    feed = contacts_service.GetContactsFeed()
    emails.extend(sum([[email.address for email in entry.email] for entry in feed.entry], []))
    next_link = feed.GetNextLink()
    while next_link:
        feed = contacts_service.GetContactsFeed(uri=next_link.href)
        emails.extend(sum([[email.address for email in entry.email] for entry in feed.entry], []))
        next_link = feed.GetNextLink()
    return emails

def import_contacts(request):
    if request.GET.get('token', ''):
        emails = get_contact_emails(request.GET['token'])
        users = User.objects.filter(email__in=emails)
        return render('google_contacts/results.html', {
            'users': users
        })
    else:
        next = get_full_url(request)
        return render('socialacc/login.html', {
        'auth_sub_url': get_auth_sub_url(next)
        })