from django.core.management.base import BaseCommand
from haystack.query import SearchQuerySet
from pin.models import Post, Campaign
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    def handle(self, *args, **options):
        camp = Campaign.objects.get(id=4)
        print camp.id
        campaign_tags = camp.tags
        tags = campaign_tags.split(',')
        tags.append(camp.primary_tag)
        start_date = camp.start_date.strftime("%s")
        end_date = camp.end_date.strftime("%s")

        posts = SearchQuerySet().models(Post)\
            .filter(tags__in=tags,
                    timestamp_i__gte=start_date,
                    timestamp_i__lte=end_date).order_by('-cnt_like_i')

        user_obj = {}

        for post in posts:
            try:
                post_obj = Post.objects.get(id=post.pk)
                u = str(post_obj.user.username)
                if u not in user_obj:
                    dn = {
                        "count": 1,
                        "like": int(post_obj.cnt_like)
                    }
                    user_obj[u] = dn
                else:
                    dn = user_obj[u]
                    dn["like"] += int(post_obj.cnt_like)
                    dn["count"] += 1

            except Exception:
                pass

        print sorted(user_obj, key=lambda x: user_obj[x]['like'])
