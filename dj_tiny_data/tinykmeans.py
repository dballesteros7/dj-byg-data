import sys

import matplotlib.pyplot as plt

from dj_tiny_data import paths


def main():
    # tfidf.calculate_tf_idf_matrix()
    # qm = quality_metrics.QualityMetrics()
    # with open(paths.K_MEANS_PERF_PATH, 'w') as foutput:
    #     for n in xrange(5, 101):
    #         result = kmeans.k_means(n_clusters=n)
    #         quality = qm.evaluate_kmeans(result)
    #         foutput.write('{}, {}\n'.format(str(n), str(quality)))
    with open(paths.K_MEANS_PERF_PATH, 'r') as finput:
        n_list = []
        q_list = []
        for line in finput:
            n, q = map(float, line.strip().split(',', 1))
            n_list.append(n)
            q_list.append(q)
        print n_list
        print q_list

        plt.plot(n_list, q_list, '-o')
        plt.xlim(xmin=5.0)
        plt.ylim(ymin=0.5)
        plt.xlabel('Number of clusters')
        plt.ylabel('Fraction of good clusters')
        plt.title('Fraction of good clusters for various k')
        plt.grid()
        plt.show()
        plt.savefig('test.png')


if __name__ == '__main__':
    sys.exit(main())
