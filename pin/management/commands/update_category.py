from django.core.management.base import BaseCommand
from pin.models import Post, Category, SubCategory
from haystack.query import SearchQuerySet


class Command(BaseCommand):
    def handle(self, *args, **options):
        post_of_cat = {}
        try:
            query = SearchQuerySet().models(Post).facet('category_i')
            post_of_cat = dict(query.facet_counts()['fields']['category_i'])
        except Exception as e:
            print str(e)

        for key, val, in post_of_cat.iteritems():
            cat = Category.objects.get(id=int(key))
            cat.cnt_post = val
            cat.save()
            print "Category {} updated".format(key)

        sub_cats = SubCategory.objects.all()

        for sub_cat in sub_cats:
            categoreis = Category.objects.filter(parent=sub_cat).values_list('id', flat=True)

            cnt_post = SearchQuerySet().models(Post)\
                .filter(category_i__in=categoreis).facet('category_i').count()

            sub_cat.cnt_post = cnt_post
            sub_cat.save()
            print "SubCategory {} updated".format(sub_cat.id)
