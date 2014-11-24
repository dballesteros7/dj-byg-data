import itertools
import os

from dj_byg_data import DATA_PATH
from dj_byg_data.model.connect import DBConnection
from dj_byg_data.preprocessing.sqlite.similar_songs import SimilarSong


def main():
    with open(os.path.join(
            DATA_PATH, 'similar_songs.csv'), 'w') as output_file:
        similar_songs = SimilarSong()
        with DBConnection().engine.connect() as conn:
            result = conn.execute('SELECT track_id FROM songs').fetchall()
            tracks = set(track[0] for track in result)

        similar_song_batch = similar_songs.get_batch()
        offset = 0
        similar_pairs = set()
        while similar_song_batch:
            for similar_song in similar_song_batch:
                source = similar_song['tid']
                if source not in tracks:
                    continue
                targets = similar_song['target'].split(',')
                a, b = itertools.tee(targets)
                next(b, None)
                target_weight = itertools.izip(a, b)
                for target, weight in target_weight:
                    if target in tracks:
                        sorted_tuple = tuple(sorted((source, target)))
                        if sorted_tuple not in similar_pairs:
                            output_file.write('%s,%s,%s\n' % (sorted_tuple[0],
                                                              sorted_tuple[1],
                                                              weight))
                            similar_pairs.add(sorted_tuple)
            offset += len(similar_song_batch)
            similar_song_batch = similar_songs.get_batch(offset=offset)


if __name__ == '__main__':
    main()
