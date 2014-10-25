"""A module that keep the paths to all files required in the other scripts."""
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, 'data')

MSD_TRACK_LIST = os.path.join(
    DATA_DIR, 'MillionSongSubset/AdditionalFiles/subset_unique_tracks.txt')
LASTFM_DB_PATH = os.path.join(DATA_DIR, 'lastfm_tags.db')
MXM_DB_PATH = os.path.join(DATA_DIR, 'mxm_dataset.db')

OUTPUT_FILE = os.path.join(DATA_DIR, 'tag_track_data.txt')

