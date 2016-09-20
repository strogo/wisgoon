from django.core.management.base import BaseCommand
from haystack.query import SearchQuerySet
from pin.models import Post, Campaign


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
                    timestamp_i__lte=end_date)

        user_obj = {}

        for post in posts:
            try:
                post_obj = Post.objects.get(id=post.pk)
                u = int(post_obj.user_id)
                if u in user_obj:
                    user_obj[u] += int(post_obj.cnt_like)
                else:
                    user_obj[u] = int(post_obj.cnt_like)
            except Exception:
                pass
        print user_obj

        print sorted(user_obj.items(), key=lambda x: x[1])
