import sys

from dj_tiny_data import kmeans, paths, quality_metrics, tfidf


def main():
    tfidf.calculate_tf_idf_matrix()
    qm = quality_metrics.QualityMetrics()
    with open(paths.K_MEANS_PERF_PATH, 'w') as foutput:
        for n in xrange(5, 101):
            result = kmeans.k_means(n_clusters=n)
            quality = qm.evaluate_kmeans(result)
            foutput.write('{}, {}\n'.format(str(n), str(quality)))

if __name__ == '__main__':
    sys.exit(main())
