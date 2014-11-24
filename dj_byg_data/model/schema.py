from sqlalchemy import (MetaData, Table, Column, Integer, Sequence, String,
                        ForeignKey, Float)
from sqlalchemy.dialects.postgresql import ARRAY

metadata = MetaData()

songs = Table(
    'songs', metadata,
    Column('song_id', String(200), primary_key=True),
    Column('title', String(200), nullable=False),
    Column('release', String(200), nullable=False),
    Column('artist_id', String(200), nullable=False, index=True),
    Column('lastfm_tags', ARRAY(String(100)), nullable=False))

artists = Table(
    'artists', metadata,
    Column('artist_id', String(200), primary_key=True),
    Column('artist_name', String(200), nullable=False, index=True))

similar_songs = Table(
    'similar_songs', metadata,
    Column('song_id_a', ForeignKey('songs.song_id'), primary_key=True),
    Column('song_id_b', ForeignKey('songs.song_id'), primary_key=True),
    Column('weight', Float, nullable=False, default=1.0))

similar_artists = Table(
    'similar_artists', metadata,
    Column('artist_id_a', ForeignKey('artists.artist_id'), primary_key=True),
    Column('artist_id_b', ForeignKey('artists.artist_id'), primary_key=True))

artist_terms = Table(
    'artist_terms', metadata,
    Column('term', String(500), primary_key=True))

song_artist_terms = Table(
    'song_artist_terms', metadata,
    Column('song_id', ForeignKey('songs.song_id'), primary_key=True),
    Column('term', ForeignKey('artist_terms.term'), primary_key=True))

clusters = Table(
    'clusters', metadata,
    Column('cluster_id', Integer, Sequence('cluster_id_seq'),
           primary_key=True),
    Column('center', ARRAY(Float), nullable=False),
    Column('cluster_version', String(100), nullable=False))

cluster_assignment = Table(
    'cluster_assignment', metadata,
    Column('cluster_id', ForeignKey('clusters.cluster_id'), primary_key=True),
    Column('song_id', ForeignKey('songs.song_id'), primary_key=True),
    Column('distance', Float, nullable=False))
