import requests
import json
from daddy_avatar.templatetags.daddy_avatar import get_avatar
pd = PhoneData.objects.only('google_token')\
 .get(user_id=post.user_id)

data = {
 "to": pd.google_token,
 "data": {
     "message": {
         "id": int("2%s" % comment.object_pk_id),
         "avatar_url": "http://wisgoon.com%s" % get_avatar(comment.user_id, size=100),
         "ticker": u"نظر جدید",
         "title": u"نظر داده است",
         "content": comment.comment,
         "last_actor_name": comment.user.username,
         "url": "wisgoon://wisgoon.com/pin/%s" % comment.object_pk_id,
         "is_ad": False
     }
 }
}

res = requests.post(url='https://android.googleapis.com/gcm/send',
                 data=json.dumps(data),
                 headers={'Content-Type': 'application/json',
                          'Authorization': 'key=AIzaSyAZ28bCEeqRa216NDPDRjHfF2IPC7fwkd4'})