"""This module defines several quality metrics for the produced clusters."""
from collections import defaultdict

import json

from dj_tiny_data import data_structs, errors, paths


class QualityMetrics(object):
    """Provides a set of methods that measure the quality of track clusters
    for the task of identifying music genres from lyrics.

    Attributes:
        track_file_path: The path to the file with the full information for
                         each track.
        track_index: A dictionary that indexes the tracks in the text track
                     with the full track information.
    """

    def __init__(self, track_info_path=None):
        """Initializes an instance of this class and populates the track
        index.

        If no path to the track file is given, this reads from the default
        location defined in the paths module.
        """
        self.track_index = {}
        self.track_info_path = track_info_path
        if self.track_info_path is None:
            self.track_info_path = paths.OUTPUT_FILE
        offset = 0
        with open(self.track_info_path, 'r') as track_info_file:
            for line in track_info_file:
                self.track_index[json.loads(line)['id']] = offset
                offset += len(line)

    def retrieve_track_genres(self, track_id):
        """Retrieve the information of the track with the given track_id.

        This method looks up the track in the file on disk with the genre
        information. In order to make this process efficient, this method uses
        an index built when the class was instantiated.

        Args:
            track_id: The unique ID of the track whose information is required.
        Returns:
            A Track instance matching the track ID given.
        Raises:
            NoTrackError: If there is no track on file with the given ID.
        """
        if track_id not in self.track_index:
            raise errors.NoTrackError
        with open(self.track_info_path, 'r') as track_info_file:
            track_info_file.seek(self.track_index[track_id])
            track_info_line = track_info_file.readline()
            track_info = json.loads(track_info_line)
            track = data_structs.Track(**track_info)
            return track

    def binary_genre_cluster_quality(self, cluster):
        """Evaluates a cluster and assigns it a binary judgment.

        A cluster is considered good when at least one genre is present in all
        tracks belonging to the cluster.

        Args:
            cluster: Set of track IDs that belong to a cluster.
        Returns:
            A boolean value indicating whether the given cluster is good or bad
            for identifying genres.
        """
        print 'CLUSTER ============================='
        intersecting_genres = set()
        for track_id in cluster:
            track = self.retrieve_track_genres(track_id)
            print set(track.genres)
            intersecting_genres &= set(track.genres)
        return bool(intersecting_genres)

    def majority_genre_cluster_quality(self, cluster):
        """Evaluates a cluster and assigns a binary judgment to it.

        A cluster is considered good when there is at least one genre that
        appears in strictly more than half of the tracks in the clusters.

        Args:
            cluster: Set of track IDs that belong to the cluster.
        Returns:
            A boolean indicating whether the given cluster is good or bad
            for identifying genres.
        """
        print 'CLUSTER ==========================='
        genres_count = defaultdict(int)
        for track_id in cluster:
            track = self.retrieve_track_genres(track_id)
            print set(track.genres)
            for genre in track.genres:
                genres_count[genre] += 1
        for genre in genres_count:
            threshold = len(cluster) / 2 + 1
            if genres_count[genre] > threshold:
                return True
        return False
