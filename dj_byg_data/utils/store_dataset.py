"""Tool to upload the dataset to Amazon S3."""
import json
import glob
import os
import shutil
import sys
import tarfile
import tempfile
import time
import traceback

import h5py

from dj_byg_data import DATA_PATH
from dj_byg_data.model.connect import DBConnection
from dj_byg_data.model.schema import (songs, artists, artist_terms,
                                      song_artist_terms)


def load_tracks_with_lyrics():
    tracks_with_lyrics = set()
    with open(os.path.join(
            DATA_PATH, 'tracks_with_lyrics.txt'), 'r') as lyrics:
        for line in lyrics:
            tracks_with_lyrics.add(line.strip())
    return tracks_with_lyrics


def main():
    db_conn = DBConnection()
    engine = db_conn.engine
    tracks_with_lyrics = load_tracks_with_lyrics()
    tar_files = glob.glob(os.path.join(DATA_PATH,
                                       'MillionSongDataset', '[A-Z].tar.gz'))
    lastfm_tar_files = glob.glob(os.path.join(DATA_PATH,
                                              'MillionSongDataset',
                                              '[A-Z].lastfm.tar.gz'))
    tar_files.sort()
    lastfm_tar_files.sort()
    counter = 0
    start_time = time.time()
    for tar_file_path, lastfm_tar_file_path in zip(tar_files,
                                                   lastfm_tar_files):
        tar_file = tarfile.open(tar_file_path, 'r')
        lastfm_tar_file = tarfile.open(lastfm_tar_file_path, 'r')
        next_member = tar_file.next()
        while next_member is not None:
            if next_member.isfile() and os.path.splitext(os.path.basename(
                    next_member.name))[0] in tracks_with_lyrics:
                dir_path = tempfile.mkdtemp()
                tar_file.extract(next_member, path=dir_path)
                lastfm_member_name = os.path.splitext(
                    next_member.name)[0] + '.json'
                try:
                    lastfm_file = lastfm_tar_file.extractfile(
                        lastfm_member_name)
                except KeyError:
                    lastfm_data = {'tags': []}
                else:
                    lastfm_data = json.load(lastfm_file)
                h5_file = h5py.File(
                    os.path.join(dir_path, next_member.name), 'r')
                song_data = {
                    'song_id': h5_file['metadata']['songs']['song_id'][0],
                    'artist_name':
                    h5_file['metadata']['songs']['artist_name'][0],
                    'release': h5_file['metadata']['songs']['release'][0],
                    'title': h5_file['metadata']['songs']['title'][0],
                    'artist_id': h5_file['metadata']['songs']['artist_id'][0],
                    'artist_terms':
                    list(h5_file['metadata']['artist_terms'])
                }
                conn = engine.connect()
                trans = conn.begin()
                try:
                    artist_check_stmt = artists.select().where(
                        artists.c.artist_id == song_data['artist_id'])
                    result = conn.execute(artist_check_stmt)
                    if result.fetchone() is None:
                        artist_stmt = artists.insert().values(
                            artist_id=song_data['artist_id'],
                            artist_name=song_data['artist_name'])
                        conn.execute(artist_stmt)
                    else:
                        result.close()
                    insert_song_stmt = songs.insert().values(
                        song_id=song_data['song_id'],
                        title=song_data['title'],
                        release=song_data['release'],
                        artist_id=song_data['artist_id'],
                        lastfm_tags=[tag[0] for tag in lastfm_data['tags']])
                    conn.execute(insert_song_stmt)
                    for term in song_data['artist_terms']:
                        term_check_stmt = artist_terms.select().where(
                            artist_terms.c.term == term)
                        result = conn.execute(term_check_stmt)
                        if result.fetchone() is None:
                            term_stmt = artist_terms.insert().values(
                                term=term)
                            conn.execute(term_stmt)
                        else:
                            result.close()
                        insert_term_song_stmt = song_artist_terms.insert(
                            ).values(song_id=song_data['song_id'],
                                     term=term)
                        conn.execute(insert_term_song_stmt)
                except:
                    traceback.print_exc()
                    trans.rollback()
                else:
                    trans.commit()
                    counter += 1
                    if counter % 5000 == 0:
                        print counter
                        print '%s minutes' % str((time.time() - start_time)/60)
                finally:
                    conn.close()
                h5_file.close()
                shutil.rmtree(dir_path)
            next_member = tar_file.next()
        tar_file.close()

if __name__ == '__main__':
    sys.exit(main())
