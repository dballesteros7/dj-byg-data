import sys

from dj_tiny_data import kmeans, quality_metrics, tfidf


def main():
    tfidf.calculate_tf_idf_matrix()
    result = kmeans.k_means()
    qm = quality_metrics.QualityMetrics()
    qm.evaluate_kmeans(result)

if __name__ == '__main__':
    sys.exit(main())
