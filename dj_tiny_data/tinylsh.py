import numpy as np

from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections

from paths import *
from datautils import *
from quality_metrics import QualityMetrics


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

            print qm.majority_genre_cluster_quality(neighbour_list)


if __name__ == '__main__':
    main()
