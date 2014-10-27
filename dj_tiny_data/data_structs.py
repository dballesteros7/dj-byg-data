"""Module with classes that define common data structures and
help to keep the code clean."""

import numpy as np
from scipy.sparse import csc_matrix

LYRICS_DIM = 5000

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
        self.word_count_vector = None # Evaluated lazily


    def vectorize_words(self):
        """Converts this track into a (sparse unit) vector"""
        # Evalutate the vector in a lazy manner
        if self.word_count_vector is None:
            vec_length = np.sqrt(sum([x*x for x in self.word_count.values()]))
            # self.word_count_vector = csc_matrix((LYRICS_DIM ,1))
            self.word_count_vector = np.zeros(LYRICS_DIM)
            for word_id, count in self.word_count.iteritems():
                self.word_count_vector[word_id-1] = count/vec_length # word_id initially \in [1, LYRICS_DIM)
        return self.word_count_vector
