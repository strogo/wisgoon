from django.core.management.base import BaseCommand

from pin.models import Post
from django.contrib.auth.models import User
from pin.api6.tools import post_item_json


class Command(BaseCommand):
    def handle(self, *args, **options):
        username_list = [
            "110yas",
            "hojrehmajazi",
            "Ashena110",
            "Msajad98",
            "Sobohat",
            "al-karim",
            "Mdsh1001",
            "namber",
            "Sad555",
            "ketabdar",
            "tanzoroon",
            "farzamaboofazeli",
            "Hossein.Mirmoheb",
            "Menp",
            "karandesh",
            "Fekreno",
            "Sayyade.delha",
            "Eskandar",
            "1bahar",
            "nasimnoor",
            "mantilla",
            "kalamemobin",
            "arezooye_parvaz",
            "Betti1343",
            "nasimebahari",
            "Najva139",
            "chakavakane",
            "z.we"
        ]
        users = User.objects.only('id')\
            .filter(username__in=username_list)
        for user in users:
            posts = Post.objects.only('id').filter(user_id=user.id)
            total_view = 0
            for post in posts:
                p = post_item_json(post_id=post.id, fields=['cnt_view'])
                total_view += p['cnt_view']
            print "user {} cnt_view total_view {}".format(user.id, total_view)
