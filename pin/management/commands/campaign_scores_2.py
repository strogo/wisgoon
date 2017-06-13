from django.core.management.base import BaseCommand
# from haystack.query import SearchQuerySet
from pin.models import Post, Campaign, CampaignWinners
import sys
from operator import getitem
from pin.models_es import ESPosts

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):

    def handle(self, *args, **options):
        print "camp scores"
        print "=================================="

        camp_id = options['camp_id']

        if not camp_id:
            print "Enter camp id"
            return

        camp = Campaign.objects.get(id=camp_id)
        print camp.id
        campaign_tags = camp.tags
        tags = campaign_tags.split(',')
        tags.append(camp.primary_tag)
        start_date = int(camp.start_date.strftime("%s"))
        end_date = int(camp.end_date.strftime("%s"))
        camp_limit = camp.limit

        # posts = SearchQuerySet().models(Post)\
        #     .filter(tags__in=tags,
        #             timestamp_i__gte=start_date,
        #             timestamp_i__lte=end_date).order_by('-cnt_like_i')
        ps = ESPosts()
        user_obj = {}
        status = True
        offset = 0
        limit = 100
        order_by = "cnt_like"

        while status:

            posts = ps.search_campaign(text=tags,
                                       range_date=[start_date, end_date],
                                       offset=offset,
                                       limit=limit,
                                       order=order_by)

            print "len post", len(posts)
            if len(posts) == 0:
                status = False

            offset = offset + limit

            for post in posts:
                print "post_id: ", post.id, "timestamp: ", post.timestamp
                try:
                    post_obj = Post.objects.get(id=post.id)
                    u = str(post_obj.user.username)
                    if u not in user_obj:
                        dn = {
                            "count": 1,
                            "like": int(post_obj.cnt_like)
                        }
                        user_obj[u] = dn
                    else:
                        dn = user_obj[u]
                        if camp_limit > 0:
                            if dn["count"] < camp_limit:
                                dn["like"] += int(post_obj.cnt_like)
                                dn["count"] += 1
                        else:
                            dn["like"] += int(post_obj.cnt_like)
                            dn["count"] += 1

                except Exception:
                    continue

        winners = sorted(user_obj.items(),
                         key=lambda x: getitem(x[1], 'like'),
                         reverse=True)
        # print winners

        camp_winners, created = CampaignWinners.objects\
            .get_or_create(campaign=camp)
        camp_winners.status = CampaignWinners.COMPLETED
        camp_winners.winners = winners
        camp_winners.save()
        print winners
