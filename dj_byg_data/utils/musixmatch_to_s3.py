"""Process the zipfiles that can be downloaded from the MSD - musiXmatch
website and upload them to a S3 bucket for further processing.
"""
import cStringIO as StringIO
import zipfile

from boto.s3 import connect_to_region
from boto.s3.connection import Location
from boto.s3.key import Key

TRAIN_FILENAME = 'mxm_dataset_train.txt'
TEST_FILENAME = 'mxm_dataset_test.txt'
TRAIN_FILEPATH = '/local/diegob/workspace/bigdata-2014/dj-byg-data/data/mxm_dataset_train.txt.zip'
TEST_FILEPATH = '/local/diegob/workspace/bigdata-2014/dj-byg-data/data/mxm_dataset_test.txt.zip'
S3_BUCKET = 'dj-byg-data'
MXM_S3_KEY = 'input/mxm_dataset.txt'


def main():
    output = StringIO.StringIO()
    for path, name in zip((TRAIN_FILEPATH, TEST_FILEPATH),
                          (TRAIN_FILENAME, TEST_FILENAME)):
        with zipfile.ZipFile(path, 'r') as train_zip_file:
            train_file = train_zip_file.open(name, 'r')
            train_file_lines = train_file.readlines()
            for train_line in train_file_lines:
                if train_line.startswith('#') or train_line.startswith('%'):
                    continue
                train_line_tokens = train_line.split(',', 2)
                doc_id = train_line_tokens[0]
                for term_count in train_line_tokens[2].split(','):
                    term, count = term_count.split(':', 1)
                    count = int(count)
                    assert count > 0
                    output.write('%s,%s,%d\n' % (doc_id, term, count))
    output.seek(0)

    s3_conn = connect_to_region('eu-west-1')
    bucket = s3_conn.lookup(S3_BUCKET)
    if bucket is None:
        bucket = s3_conn.create_bucket(S3_BUCKET, location=Location.EU)
    key = Key(bucket)
    key.key = MXM_S3_KEY
    key.set_contents_from_file(output)

if __name__ == '__main__':
    main()
