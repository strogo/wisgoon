from django.core.management.base import BaseCommand
from haystack.query import SearchQuerySet
from pin.models import Post, Campaign
from pin.search_indexes import PostIndex
from pin.tasks import camp_scores


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "update camp posts"
        print "=================================="
        camp_id = options['camp_id']
        if not camp_id:
            print "Enter camp_id"
            return
        try:
            campaign = Campaign.objects.get(id=camp_id)
        except:
            campaign = None

        if not campaign:
            print "camp not found"
            return

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
                print "============================================="
            except Exception as e:
                print str(e), "post_id:{}".format(post.pk)
                pass
        camp_scores.delay(camp_id=camp_id)
