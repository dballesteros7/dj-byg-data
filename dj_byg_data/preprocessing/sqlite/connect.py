from sqlalchemy import create_engine


class DBConnection(object):
    def __init__(self, database_url):
        self._engine = None
        self.database_url = database_url

    def _create_engine(self):
        self._engine = create_engine(self.database_url)

    @property
    def engine(self):
        if self._engine is None:
            self._create_engine()
        return self._engine
