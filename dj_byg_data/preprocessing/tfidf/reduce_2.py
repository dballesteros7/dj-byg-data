#!/usr/bin/python
import sys


def main():
    current_key = None
    vector_representation = [0.0 for _ in xrange(5000)]
    for line in sys.stdin:
        tokens = line.strip().split('\t', 1)
        doc_id = tokens[0]
        sub_tokens = tokens[1].split(',', 2)
        term_index = int(sub_tokens[0])
        idf = float(sub_tokens[1])
        tf = float(sub_tokens[2])
        tf_idf = tf*idf
        if current_key is None:
            current_key = doc_id
        if current_key != doc_id:
            print '%s %s' % (current_key, ','.join(str(x) for x in vector_representation))
            vector_representation = [0.0 for _ in xrange(5000)]
            current_key = doc_id
        vector_representation[term_index - 1] = tf_idf
    if current_key is not None:
        print '%s %s' % (current_key, ','.join(str(x) for x in vector_representation))

if __name__ == '__main__':
    sys.exit(main())
