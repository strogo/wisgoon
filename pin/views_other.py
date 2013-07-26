import gdata.contacts.data
from gdata.contacts.client import ContactsClient, ContactsQuery
from gdata.gauth import AuthSubToken

from django.shortcuts import render
from django.conf import settings

if settings.DEBUG:
	MAX_RESULT = 25
	PAGING = False
	TEST_PAGE_URL = 'http://127.0.0.1:8000/pin/invite/google'
else:
	MAX_RESULT = 100000
	PAGING = True
	TEST_PAGE_URL = 'http://wisgoon.com/pin/invite/google'

def GetAuthSubUrl():
    next = TEST_PAGE_URL
    scopes = ['http://www.google.com/m8/feeds/']
    secure = False  # set secure=True to request a secure AuthSub token
    session = True
    return gdata.gauth.generate_auth_sub_url(next, scopes, secure=secure, session=session)

def invite_google(request):

    all_emails = []
    if 'token' in request.GET:

        token = request.GET['token']
        token_auth_login = AuthSubToken(token)
        
        query = ContactsQuery()
        query.max_results = MAX_RESULT

        client = ContactsClient(auth_token=token_auth_login)
        client.upgrade_token(token=token_auth_login)

        try:
            feed = client.GetContacts(q=query)
            while feed:
                next = feed.GetNextLink()

                for entry in feed.entry:
                    try:
                        email_address = entry.email[0].address
                        #print email_address
                        all_emails.append(email_address)
                    except:
                        pass

                feed = None
                if PAGING and next:
                    feed = client.GetContacts(next.href, auth_token=token_auth_login, q=query)
        except:
            pass

    return render(request , 'pin/invite_google.html', {'login': GetAuthSubUrl(), 'all_emails':all_emails})
