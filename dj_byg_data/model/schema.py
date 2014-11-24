from sqlalchemy import (MetaData, Table, Column, Integer, Sequence, String,
                        ForeignKey, Float, Text)
from sqlalchemy.dialects.postgresql import ARRAY

metadata = MetaData()

songs = Table(
    'songs', metadata,
    Column('track_id', String(100), primary_key=True),
    Column('title', Text, nullable=False),
    Column('release', Text, nullable=False),
    Column('artist_id', String(100), nullable=False, index=True),
    Column('year', Integer, nullable=False, index=True),
    Column('lastfm_tags', ARRAY(Text), nullable=False))

artists = Table(
    'artists', metadata,
    Column('artist_id', String(100), primary_key=True),
    Column('artist_name', Text, nullable=False))

similar_songs = Table(
    'similar_songs', metadata,
    Column('track_id_a', ForeignKey('songs.track_id'), primary_key=True),
    Column('track_id_b', ForeignKey('songs.track_id'), primary_key=True),
    Column('weight', Float, nullable=False, default=1.0))

similar_artists = Table(
    'similar_artists', metadata,
    Column('artist_id_a', ForeignKey('artists.artist_id'), primary_key=True),
    Column('artist_id_b', ForeignKey('artists.artist_id'), primary_key=True))

terms = Table(
    'terms', metadata,
    Column('term_id', Integer, Sequence('term_id_seq'), primary_key=True),
    Column('term', Text, nullable=False))

artist_terms = Table(
    'artist_terms', metadata,
    Column('artist_id', ForeignKey('artists.artist_id'), primary_key=True),
    Column('term_id', ForeignKey('terms.term_id'), primary_key=True))

clusters = Table(
    'clusters', metadata,
    Column('cluster_id', Integer, Sequence('cluster_id_seq'),
           primary_key=True),
    Column('center', ARRAY(Float), nullable=False),
    Column('cluster_version', String(100), nullable=False))

cluster_assignment = Table(
    'cluster_assignment', metadata,
    Column('cluster_id', ForeignKey('clusters.cluster_id'), primary_key=True,
           index=True),
    Column('track_id', ForeignKey('songs.track_id'), primary_key=True,
           index=True),
    Column('distance', Float, nullable=False))

stemmed_lyrics = Table(
    'stemmed_lyrics', metadata,
    Column('word_id', Integer, primary_key=True),
    Column('word', String(500), nullable=False))

word_counts = Table(
    'word_counts', metadata,
    Column('track_id', ForeignKey('songs.track_id'), nullable=False,
           primary_key=True, index=True),
    Column('word_id', ForeignKey('stemmed_lyrics.word_id'), nullable=False,
           primary_key=True, index=True),
    Column('count', Integer, nullable=False, default=0))
