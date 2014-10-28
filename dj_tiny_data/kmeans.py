"""K-Means clustering for the tracks."""
import numpy as np

from sklearn.cluster import KMeans

from dj_tiny_data import paths


def k_means(input_matrix_path=paths.TF_IDF_MATRIX_PATH):
    km_solve = KMeans(n_clusters=100, n_init=10,
                      max_iter=500, tol=1e-6)
    tf_idf = np.loadtxt(input_matrix_path, delimiter=',')
    km_solve.fit(tf_idf)
    return km_solve
