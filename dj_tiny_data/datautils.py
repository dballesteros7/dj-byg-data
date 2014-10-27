"""
A bunch of commonly used helper functions
"""
import jellyfish
import yaml
import json

from paths import *
from data_structs import Track

def _load_clean_genres():
    """Auxiliary function to load the file with the clean genre list and
    parse it to a python dictionary. Original format is YAML.
    """
    with open(GENRE_LIST_PATH, 'r') as fgenre:
        genres = yaml.load(fgenre)
    return genres


def cache_clean_genres(func):
    """Decorator that caches the file with the manually selected music
    genres, this avoids opening the file everytime a tag lookup is needed.
    """
    cache = {}

    def _wrapper(tag):
        if 'clean_genres' not in cache:
            cache['clean_genres'] = _load_clean_genres()
        return func(tag, cache['clean_genres'])
    return _wrapper


@cache_clean_genres
def tag_to_genre(tag, clean_genres):
    """Clean the tag by searching for a match in the canonical list of genres.
    This returns None if no suitable match is found.
    """
    tag = tag.encode('ascii', 'replace').lower()
    for genre in clean_genres:
        search_genre = genre.lower()
        dl_distance = jellyfish.damerau_levenshtein_distance(
            search_genre, tag)
        if dl_distance <= 1:
            return genre
        for subgenre in clean_genres[genre]:
            subgenre_search = subgenre.lower()
            dl_distance = jellyfish.damerau_levenshtein_distance(
                subgenre_search, tag)
            if dl_distance <= 1:
                return genre
    return None


def json_line_to_track(line):
    """Converts a json line to an appropriate Track object
    """
    track_dct = json.loads(line)
    # Clean up word count dictionary
    wc_dct = {}
    for word_id, word_count in track_dct['wordcount'].iteritems():
        wc_dct[int(word_id)] = int(word_count)
    track = Track(track_dct['id'], track_dct['genres'], wc_dct)
    return track
