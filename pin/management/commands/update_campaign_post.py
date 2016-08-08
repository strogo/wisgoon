from django.core.management.base import BaseCommand
from haystack.query import SearchQuerySet
from pin.models import Post, Campaign
# from pin.search_indexes import PostIndex


class Command(BaseCommand):
    def handle(self, *args, **options):
        campaigns = Campaign.objects.filter(is_current=True, expired=False).order_by('-id')
        for campaign in campaigns:
            campaign_tags = campaign.tags
            tags = campaign_tags.split(',')
            tags.append(campaign.primary_tag)
            start_date = campaign.start_date.strftime("%s")
            end_date = campaign.end_date.strftime("%s")

            posts = SearchQuerySet().models(Post).filter(tags__in=tags)\
                .filter(timestamp_i__lte=end_date).filter(timestamp_i__gte=start_date)\
                .order_by('-cnt_like_i')

            for post in posts:
                # post_index = PostIndex()
                post_obj = Post.objects.get(id=post.pk)
                # post_index.update_object(post_obj)
                print "solr_cnt_like: ", post.cnt_like_i
                print "cache_cnt_like: ", post_obj.cnt_like
                print "=================================================="
