from django.core.management.base import BaseCommand

from pin.models import Post
from django.contrib.auth.models import User
from pin.api6.tools import post_item_json


class Command(BaseCommand):
    def handle(self, *args, **options):
        username_list = [
            "sobhansaeed",
            "tab80",
            "nasimebahari",
            "Hossein.Mirmoheb",
            "Sobohat",
            "z.we",
            "mantilla",
            "Sad555",
            "karandesh",
            "al-karim",
            "Msajad98",
            "Fekreno",
            "Sayyade.delha",
            "110yas",
            "Betti1343",
            "Ashena110",
            "arezooye_parvaz",
            "ketabdar",
            "Najva139",
            "chakavakane",
            "namber",
            "Menp",
            "Mdsh1001",
            "nasimnoor",
            "kalamemobin",
            "Eskandar",
            "1bahar",
            "ghadremotlagh",
            "hojrehmajazi",
            "Tanzoroon",
            "Bayanmanavi",
            "tanzoroon_ir",
            "rohamaa",
            "farzamaboofazeli",
        ]
        users = User.objects.only('id', 'username')\
            .filter(username__in=username_list)
        result = []
        for user in users:
            data = {}
            posts = Post.objects.only('id').filter(user_id=user.id)

            total_view = 0
            for post in posts:
                p = post_item_json(post_id=post.id, fields=['cnt_view'])
                total_view += p['cnt_view']

            data['total_view'] = total_view
            data['username'] = user.username
            result.append(data)
        print result
