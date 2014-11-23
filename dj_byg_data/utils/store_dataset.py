"""Tool to upload the dataset to Amazon S3."""

from boto.s3 import connect_to_region
from boto.s3.connection import Location
from boto.s3.key import Key

import json
import sys
import shutil
import h5py
import tarfile
import tempfile
import glob
import os
import zipfile

DATA_DIR = '/local/diegob/workspace/bigdata-2014/dj-byg-data/data/'
S3_BUCKET = 'dj-byg-data'
DATA_PREFIX = 'songs_data/'


def load_tracks_with_lyrics():
    tracks_with_lyrics = set()
    with open(os.path.join(DATA_DIR, 'tracks_with_lyrics.txt'), 'r') as lyrics:
        for line in lyrics:
            tracks_with_lyrics.add(line.strip())
    return tracks_with_lyrics


def load_zipfiles():
    zipfile_train = zipfile.ZipFile(
        os.path.join(DATA_DIR, 'lastfm_train.zip'), 'r')
    zipfile_test = zipfile.ZipFile(
        os.path.join(DATA_DIR, 'lastfm_test.zip'), 'r')
    return zipfile_train, zipfile_test


def main():
    s3_connection = connect_to_region('eu-west-1')
    bucket = s3_connection.lookup(S3_BUCKET)
    if bucket is None:
        bucket = s3_connection.create_bucket(S3_BUCKET, location=Location.EU)
    tracks_with_lyrics = load_tracks_with_lyrics()
    zipfile_train, zipfile_test = load_zipfiles()
    tar_files = glob.glob(DATA_DIR + 'MillionSongDataset/[A-Z].tar.gz')
    for tar_file_path in tar_files:
        tar_file = tarfile.open(tar_file_path, 'r')
        next_member = tar_file.next()
        while next_member is not None:
            if next_member.isfile() and os.path.splitext(os.path.basename(
                    next_member.name))[0] in tracks_with_lyrics:
                lastfm_file_train = os.path.join(
                    'lastfm_train', os.path.splitext(next_member.name)[0] +
                    '.json')
                lastfm_file_test = os.path.join(
                    'lastfm_test', os.path.splitext(next_member.name)[0] +
                    '.json')
                try:
                    lastfm_file = zipfile_train.open(lastfm_file_train, 'r')
                except KeyError:
                    try:
                        lastfm_file = zipfile_test.open(lastfm_file_test, 'r')
                    except KeyError:
                        lastfm_data = {'tags': [], 'similars': []}
                    else:
                        lastfm_data = json.load(lastfm_file)
                else:
                    lastfm_data = json.load(lastfm_file)
                lastfm_file.close()
                dir_path = tempfile.mkdtemp()
                tar_file.extract(next_member, path=dir_path)
                h5_file = h5py.File(
                    os.path.join(dir_path, next_member.name), 'r')
                song_data = {
                    'artist_name':
                    h5_file['metadata']['songs']['artist_name'][0],
                    'release': h5_file['metadata']['songs']['release'][0],
                    'title': h5_file['metadata']['songs']['title'][0],
                    'artist_id': h5_file['metadata']['songs']['artist_id'][0],
                    'artist_terms':
                    list(h5_file['metadata']['artist_terms']),
                    'tags': lastfm_data['tags'],
                    'similar_songs': lastfm_data['similars']
                }
                key = Key(bucket)
                key.key = DATA_PREFIX + h5_file[
                    'metadata']['songs']['song_id'][0]
                key.set_contents_from_string(json.dumps(song_data))
                h5_file.close()
                shutil.rmtree(dir_path)
            next_member = tar_file.next()
        tar_file.close()
    zipfile_train.close()
    zipfile_test.close()
if __name__ == '__main__':
    sys.exit(main())
