import os

from dj_byg_data import DATA_PATH
from dj_byg_data.model.connect import DBConnection
from dj_byg_data.preprocessing.sqlite.artist_terms import ArtistTerm


def store_terms():
    with open(os.path.join(
            DATA_PATH, 'terms.csv'), 'w') as output_file_terms:

        artist_terms = ArtistTerm()
        with DBConnection().engine.connect() as conn:
            result = conn.execute('SELECT artist_id FROM artists').fetchall()
            artists = set(artist[0] for artist in result)

        artist_terms_batch = artist_terms.get_batch()
        offset = 0
        terms = set()
        while artist_terms_batch:
            for artist_term in artist_terms_batch:
                if artist_term['artist_id'] in artists:
                    if artist_term['term'] not in terms:
                        terms.add(artist_term['term'])
                        output_file_terms.write('%s\n' % artist_term['term'])
            offset += len(artist_terms_batch)
            artist_terms_batch = artist_terms.get_batch(offset=offset)


def store_artist_terms():
    with DBConnection().engine.connect() as conn:
        result = conn.execute('SELECT artist_id FROM artists').fetchall()
        artists = set(artist[0] for artist in result)
        result = conn.execute('SELECT term_id, term FROM terms').fetchall()
        terms = dict(term_tuple[::-1] for term_tuple in result)

    artist_terms = ArtistTerm()
    offset = 0
    with open(os.path.join(
            DATA_PATH, 'artist_terms.csv'), 'w') as output_file:
        artist_terms_batch = artist_terms.get_batch()
        while artist_terms_batch:
            for artist_term in artist_terms_batch:
                if artist_term['artist_id'] in artists:
                    output_file.write('%s,%s\n' % (artist_term['artist_id'],
                                                   terms[artist_term['term']]))
            offset += len(artist_terms_batch)
            artist_terms_batch = artist_terms.get_batch(offset=offset)


def main():
    #store_terms()
    store_artist_terms()


if __name__ == '__main__':
    main()
