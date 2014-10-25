"""
A bunch of commonly used helper functions
"""
import jellyfish
import yaml

from paths import *


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
    """
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
                return subgenre
    return None
