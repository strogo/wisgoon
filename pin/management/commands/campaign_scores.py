from django.core.management.base import BaseCommand
from haystack.query import SearchQuerySet
from pin.models import Post, Campaign, CampaignWinners
import sys
from operator import getitem

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "camp scores"
        print "=================================="

        # camp_id = options['camp_id']
        # camp_id = raw_input("Enter camp id: ")
        # try:
        #     camp_id = int(camp_id)
        # except:
        #     camp_id = None

        # if not camp_id:
        #     print "Enter camp id"
        #     return

        camp = Campaign.objects.get(id=6)
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

        print "len post", len(posts)

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

        winners = sorted(user_obj.items(),
                         key=lambda x: getitem(x[1], 'like'),
                         reverse=True)
        print winners

        camp_winners, created = CampaignWinners.objects\
            .get_or_create(campaign=camp)
        camp_winners.status = CampaignWinners.COMPLETED
        camp_winners.winners = winners
        camp_winners.save()
