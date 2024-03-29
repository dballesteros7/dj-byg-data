"""
Given:
1. Last.fm Dataset
2. Million Song Dataset
3. Lexicon for lyrics
Generates a file, each line containing the json:
{
    "id" : "TRAAAFD128F92F423A",
    "wordcount": { <wordid> : <normalized_count>, ...},
    "genre": [ "genre1", "genre2", .. ]
}
"""
import json
import sqlite3

from datautils import *
from paths import *


def to_write_or_not_to_write(track_data):
    '''Tracks are sometimes dirty, without any tags, or lyrics.
    So ,choose when to write.'''
    return (len(track_data['wordcount']) > 10 and
            len(track_data['genres']) > 0)


def main():
    lastfm_conn = sqlite3.connect(LASTFM_DB_PATH)
    mxm_conn = sqlite3.connect(MXM_DB_PATH)

    tracks_processed = 0
    tracks_written = 0

    with open(MSD_TRACK_LIST, 'r') as ftracks,\
            open(OUTPUT_FILE, 'w') as outfile:
        for line in ftracks:
            # Need to construct this dictionary and write to file as a json
            track_data = {
                'id': None,
                'wordcount': {},
                'genres': set()
            }
            # 1. Get the track ID
            track_id, song_id, artist_name, song_title = line.split('<SEP>')
            track_data['id'] = track_id

            # print '-' * 80
            # print 'Processing Track:', track_id
            # print '-' * 80

            # 2. Search for the list of last.fm tags associated with this song
            tag_query = """SELECT tags.tag, tid_tag.val
                           FROM tid_tag, tids, tags
                           WHERE tags.ROWID=tid_tag.tag AND
                                 tid_tag.tid=tids.ROWID AND
                                 tids.tid='%s'""" % track_id
            res = lastfm_conn.execute(tag_query)
            tag_data = res.fetchall()
            # print tag_data
            for tag, score in tag_data:
                genre, subgenre = tag_to_genre(tag)
                if genre is not None:
                    track_data['genres'].add(genre)

            # 3. Obtain the (stemmed) words and their counts for this track
            wc_query = """SELECT words.ROWID, lyrics.word, lyrics.count
                          FROM lyrics, words
                          WHERE lyrics.word = words.word AND
                                track_id = '%s'""" % track_id
            res = mxm_conn.execute(wc_query)
            wc_data = res.fetchall()  # Retrieves a list of tuples
                                      # (word_id, word, word_count)
            # print wc_data
            for word_id, word, word_count in wc_data:
                track_data['wordcount'][word] = word_count

            # print track_data

            # 4. Write to file this data as a json
            if to_write_or_not_to_write(track_data):
                track_data['genres'] = list(track_data['genres'])
                json_str = json.dumps(track_data, separators=(',', ':'))
                outfile.write('%s\n' % json_str)
                tracks_written += 1

            tracks_processed += 1

    print 'Processed %d files' % tracks_processed
    print 'Written %d files to %s' % (tracks_written, OUTPUT_FILE)

    lastfm_conn.close()
    mxm_conn.close()

if __name__ == '__main__':
    main()
