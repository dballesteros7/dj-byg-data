import os

from dj_byg_data import DATA_PATH
from dj_byg_data.preprocessing.sqlite.connect import DBConnection


class SimilarSong(DBConnection):
    def __init__(self):
        super(SimilarSong, self).__init__(
            'sqlite:///' + os.path.join(
                DATA_PATH, 'MillionSongDataset',
                'AdditionalFiles', 'lastfm_similars.db'))

    def get_batch(self, limit=100000, offset=0):
        with self.engine.connect() as conn:
            result = conn.execute("""
                SELECT * FROM similars_src
                LIMIT %d OFFSET %d""" % (limit, offset))
            return self.format_dict(result)


if __name__ == '__main__':
    similar_song = SimilarSong()
    print similar_song.get_batch()[:10]
