"""K-Means clustering for the tracks."""
import numpy as np

from sklearn.cluster import KMeans

from dj_tiny_data import paths


def k_means(input_matrix_path=paths.TF_IDF_MATRIX_PATH,
            **kwargs):
    kwargs.setdefault('tol', 1e-6)
    kwargs.setdefault('n_init', 5)
    kwargs.setdefault('max_iter', 500)
    kwargs.setdefault('n_clusters', 100)
    km_solve = KMeans(**kwargs)
    tf_idf = np.loadtxt(input_matrix_path, delimiter=',')
    km_solve.fit(tf_idf)
    return km_solve
