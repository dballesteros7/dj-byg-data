#!/usr/bin/python
import sys


def main():
    for line in sys.stdin:
        tokens = line.strip().split(',', 1)
        print '%s\t%s' % (tokens[0], tokens[1])

if __name__ == '__main__':
    sys.exit(main())
