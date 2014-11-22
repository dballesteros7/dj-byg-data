#!/usr/bin/python
import sys


def main():
    for line in sys.stdin:
        line = line.strip()
        tokens = line.split(',')
        term_id = tokens[1]
        doc_id = tokens[0]
        term_count = int(tokens[2])
        print '%s\t%s,%d' % (term_id, doc_id, term_count)


if __name__ == '__main__':
    sys.exit(main())
