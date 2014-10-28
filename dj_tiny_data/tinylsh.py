import numpy as np

from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections

from paths import *
from datautils import *
from quality_metrics import QualityMetrics

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats, math

import seaborn as sns


def mean_confidence_interval(data):
    n, min_max, mean, var, skew, kurt = scipy.stats.describe(data)
    std = math.sqrt(var)
    l, h = scipy.stats.norm.interval(0.05, loc=mean, scale=std)
    return (l, h)


def run_expt(lshashes):
    dimension = 5000
    # Create engine with pipeline configuration
    engine = Engine(dimension, lshashes=lshashes)
    list_of_clusters = []
    
    # Create LSH table
    with open(OUTPUT_FILE, 'r') as tagfile:
        for line in tagfile:
            track = json_line_to_track(line)
            engine.store_vector(track.vectorize_words(), data=track.track_id)

    # For each track query nearest neighbours and print them to a file
    with open(OUTPUT_FILE, 'r') as tagfile:
        for line in tagfile:
            track = json_line_to_track(line)
            query = track.vectorize_words()
            neighbours = engine.neighbours(query)

            neighbour_list = [x[1] for x in neighbours]
            list_of_clusters += [neighbour_list, ]

    return list_of_clusters


def evaluate():
    num_expt = 10
    qm = QualityMetrics()

    x = []
    y = []
    ylow = []
    yhigh = []
    y_clus_size = []
    y_clus_num = []

    for xi in np.arange(0.1, 1.1, 0.1):
        x += [xi, ]
        yi = []
        for i in range(num_expt):
            rbp = RandomBinaryProjections('rbp', 10)
            lshashes = [rbp]
            list_of_clusters = run_expt(lshashes)
            eval_res = [qm.majority_genre_cluster_quality(cluster, maj_prob=xi) for cluster in list_of_clusters]
            true_frac = eval_res.count(True) / float(len(eval_res))
            yi += [true_frac, ]
            y_clus_size += [len(cl) for cl in list_of_clusters]
            y_clus_num += [len(list_of_clusters), ]

        # print "=" * 50
        # print "=== ", "maj_prob = ", xi
        # print "=" * 50
        # print "Number of clusters = ", np.mean(y_clus_num)
        # print "Average cluster size = ", np.mean(y_clus_size)
        # print "Overlap fraction = ", np.mean(yi)
        
        y += [np.mean(yi), ]
        l, h = mean_confidence_interval(yi)
        ylow += [l, ]
        yhigh += [h, ]

    plt.xlim(xmin=0.0)
    plt.ylim(ymin=0.0)

    print x, y
    plt.plot(x, y, 'o-')
    plt.fill_between(x, ylow, yhigh, alpha=0.5)

    plt.xlabel('Overlap probability')
    plt.ylabel('Fraction of clusters')
    plt.title('Fraction of detected clusters with overlapping majority genre')
    plt.grid()
    plt.show()


def main():
    dimension = 5000
    rbp = RandomBinaryProjections('rbp', 10)
    # Create engine with pipeline configuration
    engine = Engine(dimension, lshashes=[rbp])

    # For evaluation
    qm = QualityMetrics()

    # Create LSH table
    with open(OUTPUT_FILE, 'r') as tagfile:
        for line in tagfile:
            track = json_line_to_track(line)
            engine.store_vector(track.vectorize_words(), data=track.track_id)

    # For each track query nearest neighbours and print them to a file
    with open(OUTPUT_FILE, 'r') as tagfile, open(LSH_CLUSTER_FILE, 'w') as lsh_f:
        for line in tagfile:
            track = json_line_to_track(line)
            query = track.vectorize_words()
            neighbours = engine.neighbours(query)

            neighbour_list = [x[1] for x in neighbours]
            lsh_f.write("%s\n" % ','.join(neighbour_list))

            print qm.majority_genre_cluster_quality(neighbour_list, maj_prob=0.75)


if __name__ == '__main__':
    evaluate()
