"""This module defines several quality metrics for the produced clusters."""
from collections import defaultdict

import json

from dj_tiny_data import data_structs, errors, paths


K_MEANS_REPORT_TEMPLATE = """
===============================================================================
K-Means Quality Report
===============================================================================
Number of tracks clustered: {n_tracks}
Number of clusters:         {n_clusters}

===============================================================================
Cluster with absolute genre:   {n_great_clusters} out of {n_clusters}
Clusters with majority genres: {n_good_clusters} out of {n_clusters}
Cluster inertia:               {cluster_inertia}
Mean cluster distance (max is 2): {mean_cluster_inertia}

Genres per cluster (where majority is present):
{genres_info}
===============================================================================
"""
CLUSTER_TEMPLATE = """Cluster {i_cluster} is of genre {genre} by majority."""
NO_CLUSTER_TEMPLATE = """Cluster {i_cluster} has no majority genre."""


class QualityMetrics(object):
    """Provides a set of methods that measure the quality of track clusters
    for the task of identifying music genres from lyrics.

    Attributes:
        track_file_path: The path to the file with the full information for
                         each track.
        track_index: A dictionary that indexes the tracks in the text track
                     with the full track information.
        track_list: A list with the ordered track IDs present in the track
                    info file.
    """

    def __init__(self, track_info_path=None):
        """Initializes an instance of this class and populates the track
        index.

        If no path to the track file is given, this reads from the default
        location defined in the paths module.
        """
        self.track_index = {}
        self.track_list = []
        self.track_info_path = track_info_path
        if self.track_info_path is None:
            self.track_info_path = paths.OUTPUT_FILE
        offset = 0
        with open(self.track_info_path, 'r') as track_info_file:
            for line in track_info_file:
                track_info = json.loads(line)
                self.track_index[track_info['id']] = offset
                self.track_list.append(track_info['id'])
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

    def absolute_genre_cluster_quality(self, cluster):
        """Evaluates a cluster and assigns it a binary judgment.

        A cluster is considered good when at least one genre is present in all
        tracks belonging to the cluster.

        Args:
            cluster: Set of track IDs that belong to a cluster.
        Returns:
            A boolean value indicating whether the given cluster is good or bad
            for identifying genres.
        """
        for _, prob in self.genre_probabilities(cluster):
            if prob == 1.0:
                return True
        return False

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
        for _, prob in self.genre_probabilities(cluster):
            if prob > 0.5:
                return True
        return False

    def genre_probabilities(self, cluster):
        """Estimates the probability of genres inside the cluster.

        This uses a ML estimator to determine how likely is each genre
        present in the cluster's tracks to identify the cluster as whole.

        Args:
            cluster: Set of track IDs that belong to the cluster.
        Returns:
            Ordered list of pairs with each genre and their estimated
            probability.
        """
        genres = defaultdict(float)
        for track_id in cluster:
            track = self.retrieve_track_genres(track_id)
            for genre in track.genres:
                genres[genre] += 1
        sorted_genres = sorted(genres.items(), key=lambda x: x[1])
        return map(lambda x: (x[0], x[1] / len(cluster)), sorted_genres)

    def evaluate_kmeans(self, fitted_kmeans):
        """Evaluate a full run of K-means and print out a quality report."""
        clusters = defaultdict(list)
        for track_id, label in zip(self.track_list, fitted_kmeans.labels_):
            clusters[label].append(track_id)
        n_good_clusters = 0
        n_great_clusters = 0
        genres_info = []
        for label in clusters:
            if self.majority_genre_cluster_quality(clusters[label]):
                n_good_clusters += 1
                genres_info.append(CLUSTER_TEMPLATE.format(
                    i_cluster=label,
                    genre=self.genre_probabilities(clusters[label])[-1]))
                if self.absolute_genre_cluster_quality(clusters[label]):
                    n_great_clusters += 1
            else:
                genres_info.append(NO_CLUSTER_TEMPLATE.format(i_cluster=label))
        genres_info_str = '\n'.join(genres_info)
        print K_MEANS_REPORT_TEMPLATE.format(
            n_tracks=len(self.track_list), n_clusters=len(clusters),
            n_good_clusters=n_good_clusters, n_great_clusters=n_great_clusters,
            cluster_inertia=fitted_kmeans.inertia_,
            mean_cluster_inertia=fitted_kmeans.inertia_/len(self.track_list),
            genres_info=genres_info_str)
