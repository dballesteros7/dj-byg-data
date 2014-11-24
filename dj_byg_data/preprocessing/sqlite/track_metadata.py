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
        conn = self.engine.connect()
        result = conn.execute(
            'SELECT * FROM songs LIMIT %d OFFSET %d' % (limit, offset))
        return result.fetchall()

if __name__ == '__main__':
    tracks = TrackMetadata()
    print tracks.get_batch()[-1]
    print tracks.get_batch(offset=1000)[-1]
