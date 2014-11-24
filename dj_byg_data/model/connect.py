from sqlalchemy import create_engine

from dj_byg_data.model import schema


class DBConnection(object):

    def __init__(self):
        self._engine = None

    def _create_engine(self):
        self._engine = create_engine(
            'postgresql://bygdata:bygdata123@bygdata.coenedpltb6x.eu-west-1'
            '.rds.amazonaws.com/bygdata')

    @property
    def engine(self):
        if self._engine is None:
            self._create_engine()
        return self._engine

    def deploy_schema(self):
        schema.metadata.create_all(bind=self.engine)

    def destroy(self):
        schema.metadata.drop_all(bind=self.engine)


if __name__ == '__main__':
    dbconn = DBConnection()
    dbconn.deploy_schema()
