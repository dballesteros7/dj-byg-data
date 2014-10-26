"""Module with classes that define common data structures and
help to keep the code clean."""


class Track(object):
    """A structure containing all the relevant information related to a track.

    Attributes:
        track_id: A unique string ID that identifies the track.
        genres: A list of genres associated with the track.
        wordcount: A dictionary with the counts of occurrences for the words
                   present in the track.
    """

    def __init__(self, id, genres, wordcount):
        self.track_id = id
        self.genres = genres
        self.word_count = wordcount
