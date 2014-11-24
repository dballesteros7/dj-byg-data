import os

from dj_byg_data import DATA_PATH
from dj_byg_data.preprocessing.sqlite.connect import DBConnection


class TrackMetadata(DBConnection):
    def __init__(self):
        super(TrackMetadata, self).__init__(
            'sqlite:///' + os.path.join(
                DATA_PATH, 'MillionSongDataset',
                'AdditionalFiles', 'track_metadata.db'))

    def get_batch(self, limit=1000, offset=0):
        with self.engine.connect() as conn:
            result = conn.execute("""
                SELECT songs.* FROM songs
                LIMIT %d OFFSET %d""" % (limit, offset))
            return self.format_dict(result)

    def format_dict(self, result_proxy):
        labels = result_proxy.keys()
        return [dict(zip(labels, result))
                for result in result_proxy.fetchall()]

if __name__ == '__main__':
    tracks = TrackMetadata()
    print tracks.get_batch()[-1]
    print tracks.get_batch(offset=1000)[-1]
    print tracks.get_batch(offset=1000000)
