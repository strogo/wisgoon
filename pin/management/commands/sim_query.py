from django.core.management.base import BaseCommand
from pin.models import Post, Sim
import numpy as np


def search(qf, limit=10):
    results = {}

    for row in Sim.objects.all()[:1000]:
        features = [float(x) for x in row.features.split(',')]
        if features == qf:
            continue
        d = chi2_distance(features, qf)
        results[row.post_id] = d

    results = sorted([(v, k) for (k, v) in results.items()])

    return results[:limit]


def chi2_distance(hist_a, hist_b, eps=1e-10):
    # compute the chi-squared distance
    hzip = zip(hist_a, hist_b)
    d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in hzip])

    # return the chi-squared distance
    return d


class Command(BaseCommand):
    
    args = '<poll_id poll_id ...>'

    def handle(self, *args, **options):

        print options, args
        p = Post.objects.get(id=60)
        features = [float(x) for x in p.sim.features.split(',')]
        results = search(features)

        for (score, resultID) in results:
            print resultID, score
