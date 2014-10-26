"""Takes the JSON file generated by the raw_to_json script and generates a
TF-IDF sparse matrix.

Note, this requires numpy and scipy.
"""
import collections
import math
import json
import sys

import numpy as np
from scipy.sparse import csc_matrix
from sklearn.cluster import AffinityPropagation

from dj_tiny_data import paths, quality_metrics


def main():
    with open(paths.OUTPUT_FILE, 'r') as finput:
        word_id_map = {}
        word_id_idx = 0
        track_array = []
        for line in finput:
            track_info = json.loads(line)
            for word_id in track_info['wordcount']:
                if word_id not in word_id_map:
                    word_id_map[word_id] = {
                        'array_index': word_id_idx,
                        'total_count': 0,
                        # 'track_count': {}
                    }
                    word_id_idx += 1
                word_id_map[word_id]['total_count'] += 1
            track_array.append(track_info)
        tf_idf_dense = np.zeros((len(track_array), len(word_id_map)))
        track_array_length = float(len(track_array))
        for idx, track in enumerate(track_array):
            track_row = tf_idf_dense[idx]
            for word_id in track_info['wordcount']:
                tf = math.sqrt(int(track_info['wordcount'][word_id]))
                idf = 1 + math.log(track_array_length /
                                   (word_id_map[word_id]['total_count'] + 1))
                track_row[word_id_map[word_id]['array_index']] = tf*idf
        tf_idf = csc_matrix(tf_idf_dense)
        ap = AffinityPropagation(max_iter=10000, convergence_iter=20)
        ap.fit(tf_idf)
        label_dict = collections.defaultdict(list)
        for idx, label in enumerate(ap.labels_):
            label_dict[label].append(track_array[idx]['id'])
        quality = quality_metrics.QualityMetrics()
        for label in label_dict:
            print quality.binary_genre_cluster_quality(label_dict[label])

if __name__ == '__main__':
    sys.exit(main())
