"""Update song-cluster mapping from output of Spark ClusterApp
"""
from boto.s3 import connect_to_region
from boto.s3.connection import Location
from boto.s3.key import Key

import numpy as np
from scipy.spatial import distance

import argparse, sys

from dj_byg_data.model.connect import DBConnection
from dj_byg_data.model.schema import clusters, cluster_assignment

S3_BUCKET = 'dj-byg-data'

CENTER_CSV_OUT = '/tmp/center.csv'
ASSIGNMENT_CSV_OUT = '/tmp/assgn.csv'


def main():
    # Read the keys for cluster center and cluster-assignments
    parser = argparse.ArgumentParser(description='Update database with respective cluster assignments')
    parser.add_argument('cluster_center_key', help='Directory containing (ClusterID -> ClusterCenter) mapping')
    parser.add_argument('cluster_assignment_key', help='Directory containing (SongID -> ClusterID) mapping')
    args = parser.parse_args()

    cluster_center_key = args.cluster_center_key
    cluster_assignment_key = args.cluster_assignment_key

    s3_conn = connect_to_region('eu-west-1')
    outbucket = s3_conn.get_bucket(S3_BUCKET)

    # Check if the specified keys actually exist
    for key in [cluster_center_key, cluster_assignment_key]:
        fold_key = key + '_$folder$' # Boto doesn't seem to understand a directory as a key. Hence, this.
        if outbucket.get_key(fold_key) is None:
            sys.exit('Key %s does not exist in bucket %s' % (key, S3_BUCKET))


    # Get the list of all cluster-cluster_center mapping
    center_mapping = {}
    with open(CENTER_CSV_OUT, 'w') as fout:
        for key in outbucket.list(cluster_center_key):
            line = key.get_contents_as_string().strip()
            if line != '':
                _cid, _cvec = line.split(' ')
                cid = int(_cid)
                cvec = map(float, _cvec.split(','))
                center_mapping[cid] = np.array(cvec)
                fout.write('%d,"{%s}",%s\n' % (cid, _cvec, '5'))

    with open(ASSIGNMENT_CSV_OUT, 'w') as fout:
        for key in outbucket.list(cluster_assignment_key):
            entries = key.get_contents_as_string()

            for _line in entries.split('\n'):
                line = _line.strip()
                if line != '':
                    a_dct = {}
                    song_id, _cid = line.split(' ')[:2]
                    cid = int(_cid)

                    fout.write('%d,%s,%f\n' % (cid, song_id, 0.0))


if __name__ == '__main__':
    main()
