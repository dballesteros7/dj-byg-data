#!/usr/bin/python
import math
import sys

DOC_NUMBER = 237662.0


def idf(df):
    return math.log(DOC_NUMBER / (df + 1)) + 1


def tf(term_freq):
    return math.sqrt(float(term_freq))


def main():
    current_key = None
    document_frequency = 0
    term_frequencies = {}
    for line in sys.stdin:
        tokens = line.strip().split('\t', 1)
        term_id = tokens[0]
        sub_tokens = tokens[1].split(',', 1)
        doc_id = sub_tokens[0]
        term_count = sub_tokens[1]
        if current_key is None:
            current_key = term_id
        if current_key != term_id:
            inverse_document_freq = idf(document_frequency)
            for doc_id in term_frequencies:
                print '%s,%s,%f,%f' % (doc_id, current_key,
                                       inverse_document_freq,
                                       tf(term_frequencies[doc_id]))
            term_frequencies = {}
            document_frequency = 0
            current_key = term_id
        document_frequency += 1
        term_frequencies[doc_id] = term_count
    if current_key is not None:
        inverse_document_freq = idf(document_frequency)
        for doc_id in term_frequencies:
            print '%s,%s,%f,%f' % (doc_id, current_key,
                                   inverse_document_freq,
                                   tf(term_frequencies[doc_id]))

if __name__ == '__main__':
    sys.exit(main())
