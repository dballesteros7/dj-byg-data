import copy
from dj_byg_data.model.connect import DBConnection
from dj_byg_data.model.schema import clusters, stemmed_lyrics


def main():
    db_conn = DBConnection()
    engine = db_conn.engine
    with engine.connect() as conn:
        result = db_conn.format_dict(conn.execute(clusters.select()))
        words = db_conn.format_dict(conn.execute(stemmed_lyrics.select().order_by(stemmed_lyrics.c.word_id)))
        cluster_top_words = {}
        for cluster in result:
            cluster_id = cluster['cluster_id']
            center = cluster['center']
            print len(center)
            ordered_top = sorted(enumerate(center), key=lambda x: (x[1], x[0]), reverse=True)
            top_words = set(words[score[0]]['word'] for score in ordered_top[:100])
            cluster_top_words[cluster_id] = top_words

        filtered = {}
        for cluster_id in cluster_top_words:
            filtered[cluster_id] = copy.copy(cluster_top_words[cluster_id])
            for cluster_id_b in cluster_top_words:
                if cluster_id == cluster_id_b:
                    continue
                filtered[cluster_id] -= cluster_top_words[cluster_id_b]
        for cluster_id in cluster_top_words:
            print cluster_id
            print ','.join(filtered[cluster_id])
            print '==========================================================='

if __name__ == '__main__':
    main()
