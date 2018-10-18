import argparse
from datetime import datetime, timezone, timedelta
import json
import os

from utils import timedeltas, build_index


def parse_cl_args():
    parser = argparse.ArgumentParser(
        description='Build index files for scrapped database')
    parser.add_argument(
        'path', help='Path a directory containing the scrapped database (folder 1d, 1h, etc)'
    )
    return parser.parse_args()


args = parse_cl_args()
build_index(args.path)
