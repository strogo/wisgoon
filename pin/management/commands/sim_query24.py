from django.core.management.base import BaseCommand
from django.conf import settings
from pin.models import Post, Sim
from pyimagesearch.colordescriptor import ColorDescriptor
from pyimagesearch.searcher import Searcher
import cv2
import numpy as np


class Command(BaseCommand):
    def handle(self, *args, **options):
        # initialize the image descriptor
        cd = ColorDescriptor((8, 12, 3))

        # load the query image and describe it
        p = Post.objects.get(id=127)
        im = p.get_image_500(api=True)
        image_path = settings.MEDIA_ROOT + "/" + im['url']
        query = cv2.imread(image_path)

        # query = cv2.imread(args["query"])
        features = cd.describe(query)
        print type(features), type(p.sim.features.split(','))

        features = [float(x) for x in p.sim.features.split(',')]

        # perform the search
        searcher = Searcher("index.csv")
        results = searcher.search(features)

        # loop over the results
        for (score, resultID) in results:
            print resultID, score
