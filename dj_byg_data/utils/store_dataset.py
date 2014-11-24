"""Tool to upload the dataset to Amazon S3."""
import os
import sys
import traceback


from dj_byg_data import DATA_PATH
from dj_byg_data.model.connect import DBConnection
from dj_byg_data.model.schema import songs, artists
from dj_byg_data.preprocessing.sqlite.track_metadata import TrackMetadata
from dj_byg_data.preprocessing.sqlite.lastfm_tags import LastfmTags


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
    counter = 1
    artist_cache = set()
    print 'Starting script...'
    lastfm_data = LastfmTags()
    lastfm_data.load_to_memory()
    print 'Loaded lastfm tags'
    track_data = TrackMetadata()
    track_batch = track_data.get_batch(limit=100000)
    offset = 100000
    while track_batch:
        filtered_batch = []
        artists_to_insert = []
        for track_info in track_batch:
            if track_info['track_id'] not in tracks_with_lyrics:
                continue
            tags = lastfm_data.get_tags(track_info['track_id'])
            track_info['lastfm_tags'] = tags
            if track_info['artist_id'] not in artist_cache:
                artists_to_insert.append(
                    {'artist_name': track_info['artist_name'],
                     'artist_id': track_info['artist_id']})
                artist_cache.add(track_info['artist_id'])
            to_delete = []
            for key in track_info:
                if key not in ('track_id', 'title', 'release',
                               'artist_id', 'year', 'lastfm_tags'):
                    to_delete.append(key)
            for key in to_delete:
                del track_info[key]
            filtered_batch.append(track_info)
        print 'Filtered batch, kept %d songs' % len(filtered_batch)
        print 'Found %d new artists' % len(artists_to_insert)
        conn = engine.connect()
        trans = conn.begin()
        try:
            conn.execute(artists.insert(), artists_to_insert)
            print 'Artists inserted'
            conn.execute(songs.insert(), filtered_batch)
            print 'Tracks inserted'
        except:
            traceback.print_exc()
            trans.rollback()
        else:
            trans.commit()
        finally:
            conn.close()
        print 'Processed batch number %d' % counter
        counter += 1
        offset += len(track_batch)
        track_batch = track_data.get_batch(limit=100000, offset=offset)
if __name__ == '__main__':
    sys.exit(main())
