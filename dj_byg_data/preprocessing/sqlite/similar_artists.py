import os

from dj_byg_data import DATA_PATH
from dj_byg_data.preprocessing.sqlite.connect import DBConnection


class SimilarArtist(DBConnection):
    def __init__(self):
        super(SimilarArtist, self).__init__(
            'sqlite:///' + os.path.join(
                DATA_PATH, 'MillionSongDataset',
                'AdditionalFiles', 'artist_similarity.db'))

    def get_batch(self, limit=100000, offset=0):
        with self.engine.connect() as conn:
            result = conn.execute("""
                SELECT * FROM similarity
                LIMIT %d OFFSET %d""" % (limit, offset))
            return self.format_dict(result)


if __name__ == '__main__':
    similar = SimilarArtist()
    print similar.get_batch()[:10]
