from pymongo import MongoClient
from sqlalchemy import create_engine
import psycopg2


class Mongo:
    """
    Context manager for Mongo client connections
    """

    def __init__(self, host='localhost', port='27017'):
        self.host = host
        self.port = port
        self.client = None

    def __enter__(self):
        self.client = MongoClient(f'mongodb://{self.host}:{self.port}')
        return self.client

    def __exit__(self, type, value, traceback):
        self.client.close()

    @staticmethod
    def clean_collection_name(name):
        return name.replace('/\\. "$*<>:|?', "_")


class Postgres:
    """
    Context manager for Postgres
    """

    def __init__(
            self,
            host='localhost',
            port=5432,
            dbname='fintech',
            username=None,
            password=None):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.username = username
        self.password = password
        self.engine = create_engine(
            "postgresql+psycopg2://",
            creator=self._connect)
        self.connection = None

    def _connect(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.username,
            password=self.password)

    def __enter__(self):
        self.connection = self.engine.connect()
        return self.connection

    def __exit__(self, type, value, traceback):
        self.connection.close()
