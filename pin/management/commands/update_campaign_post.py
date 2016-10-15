from django.core.management.base import BaseCommand
from haystack.query import SearchQuerySet
from pin.models import Post, Campaign
from pin.search_indexes import PostIndex


class Command(BaseCommand):
    def handle(self, *args, **options):
        camp_id = options['camp_id']
        # camp_id = raw_input("Enter camp id: ")
        # try:
        #     camp_id = int(camp_id)
        # except:
        #     camp_id = None

        if camp_id:
            try:
                campaign = Campaign.objects.get(id=camp_id)
            except:
                campaign = None
            if campaign:
                print campaign.id
                campaign_tags = campaign.tags
                tags = campaign_tags.split(',')
                tags.append(campaign.primary_tag)
                start_date = campaign.start_date.strftime("%s")

                posts = SearchQuerySet().models(Post)\
                    .filter(tags__in=tags,
                            timestamp_i__gte=start_date)\
                    .order_by('-cnt_like_i')

                for post in posts:
                    post_index = PostIndex()
                    try:
                        post_obj = Post.objects.get(id=post.pk)
                        print post_obj.cnt_like
                        print post.cnt_like_i
                        post_index.update_object(post_obj)
                        # print "post {} updated".format(post.pk)
                        print "==============================================="
                    except Exception as e:
                        print str(e), "post_id:{}".format(post.pk)
                        pass
