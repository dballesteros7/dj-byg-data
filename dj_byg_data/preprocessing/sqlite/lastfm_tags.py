from collections import defaultdict
import os

from dj_byg_data import DATA_PATH
from dj_byg_data.preprocessing.sqlite.connect import DBConnection


class LastfmTags(DBConnection):
    def __init__(self):
        super(LastfmTags, self).__init__(
            'sqlite:///' + os.path.join(
                DATA_PATH, 'MillionSongDataset',
                'AdditionalFiles', 'lastfm_tags.db'))
        self._cache = defaultdict(list)

    def load_to_memory(self):
        with self.engine.connect() as conn:
            cursor = conn.execute("""
                SELECT tids.tid, tags.tag
                FROM tid_tag
                INNER JOIN tids ON tid_tag.tid = tids.rowid
                INNER JOIN tags ON tid_tag.tag == tags.rowid""")
            result = cursor.fetchone()
            while result is not None:
                self._cache[result[0]].append(result[1])
                result = cursor.fetchone()

    def get_tags(self, track_id):
        return self._cache.get(track_id, [])

if __name__ == '__main__':
    lastfm_tags = LastfmTags()
    lastfm_tags.load_to_memory()
