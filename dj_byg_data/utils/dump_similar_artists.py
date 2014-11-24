import os

from dj_byg_data import DATA_PATH
from dj_byg_data.model.connect import DBConnection
from dj_byg_data.preprocessing.sqlite.similar_artists import SimilarArtist


def main():
    with open(os.path.join(
            DATA_PATH, 'similar_artists.csv'), 'w') as output_file:
        similar_artists = SimilarArtist()
        with DBConnection().engine.connect() as conn:
            result = conn.execute('SELECT artist_id FROM artists').fetchall()
            artists = set(artist[0] for artist in result)

        similar_artist_batch = similar_artists.get_batch()
        offset = 0
        similar_pairs = set()
        while similar_artist_batch:
            for similarity in similar_artist_batch:
                if (similarity['target'] in artists and
                        similarity['similar'] in artists):
                    ordered = tuple(sorted(similarity.values()))
                    if ordered not in similar_pairs:
                        output_file.write('%s,%s\n' % ordered)
                        similar_pairs.add(ordered)

            offset += len(similar_artist_batch)
            similar_artist_batch = similar_artists.get_batch(offset=offset)


if __name__ == '__main__':
    main()
