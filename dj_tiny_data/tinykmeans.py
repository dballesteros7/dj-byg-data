# -*- coding: utf-8 -*-
from collections import defaultdict
import sys

import numpy as np

#import matplotlib.pyplot as plt

from dj_tiny_data import paths, tfidf, kmeans, raw_to_json, quality_metrics


def main():
    #raw_to_json.main()
    tfidf.calculate_tf_idf_matrix()
    result = kmeans.k_means(n_clusters=15)
    np.savetxt(paths.K_MEANS_CLUSTERS, result.cluster_centers_,
               delimiter=',')
    qm = quality_metrics.QualityMetrics()
    clusters = defaultdict(list)
    for track_id, label in zip(qm.track_list, result.labels_):
        clusters[label].append(track_id)
    with open(paths.CLUSTER_GENRES, 'w') as fgenres:
        for label in sorted(clusters.keys(), key=lambda x: int(x)):
            genre = qm.genre_probabilities(clusters[label])[-1]
            fgenres.write('%s\n' % genre[0])


    # with open(paths.K_MEANS_PERF_PATH, 'r') as finput:
    #     n_list = []
    #     q_list = []
    #     for line in finput:
    #         n, q = map(float, line.strip().split(',', 1))
    #         n_list.append(n)
    #         q_list.append(q)
    #     print n_list
    #     print q_list

    #     plt.plot(n_list, q_list, '-o')
    #     plt.xlim(xmin=5.0)
    #     plt.ylim(ymin=0.5)
    #     plt.xlabel('Number of clusters')
    #     plt.ylabel('Fraction of good clusters')
    #     plt.title('Fraction of good clusters for various k')
    #     plt.grid()
    #     plt.show()
    #     plt.savefig('test.png')


if __name__ == '__main__':
    sys.exit(main())
