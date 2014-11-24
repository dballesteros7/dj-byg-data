"""Update song-cluster mapping from output of Spark ClusterApp
"""
from boto.s3 import connect_to_region
from boto.s3.connection import Location
from boto.s3.key import Key

import numpy as np

import argparse, sys

from dj_byg_data.model.connect import DBConnection
from dj_byg_data.model.schema import clusters, cluster_assignment

S3_BUCKET = 'dj-byg-data'


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

    # Get DB instance
    db_conn = DBConnection()
    engine = db_conn.engine

    # Clear cluster_assignment and clusters table, for fresh inserts (Consider moving to upserts)

    # Get the list of all cluster-cluster_center mapping
    center_mapping = {}
    for key in outbucket.list(cluster_center_key):
        line = key.get_contents_as_string().strip()
        if line != '':
            _cid, _cvec = line.split(' ')[:2]
            cid = int(_cid)
            cvec = map(float, _cvec.split(','))
            center_mapping[cid] = cvec

    print 'Beginning insert of cluster centers'
    with engine.connect() as conn:
        with conn.begin() as trans:
            try:
                for cid in center_mapping:
                    c_dct = {}
                    c_dct['cluster_id'] = cid
                    c_dct['center'] = center_mapping[cid]
                    c_dct['cluster_version'] = str(len(center_mapping)) # Currently, just use the # of clusters

                    conn.execute(clusters.insert(), c_dct)
            except:
                trans.rollback()
                raise
            else:
                trans.commit()

    # Get the list of cluster assignments, and insert line by line
    print 'Beginning insertion of cluster assignments'
    insert = 0
    batch_size = 10000
    assignment_batch = []
    with engine.connect() as conn:
        with conn.begin() as trans:
            try:
                for key in outbucket.list(cluster_assignment_key):
                    entries = key.get_contents_as_string()

                    for _line in entries.split('\n'):
                        line = _line.strip()
                        if line != '':
                            a_dct = {}
                            song_id, _cid = line.split(' ')
                            cid = int(_cid)

                            a_dct['cluster_id'] = cid
                            a_dct['track_id'] = song_id
                            a_dct['distance'] = 0.0

                            assignment_batch += [a_dct]
                            insert += 1

                            if (insert % batch_size) == 0:
                                print 'Beginning insertion of %d assignments' % batch_size
                                conn.execute(cluster_assignment.insert(), assignment_batch)
                                assignment_batch = []
                                print 'Inserted %d assignments' % batch_size
            except:
                trans.rollback()
                raise
            else:
                trans.commit()


if __name__ == '__main__':
    main()
