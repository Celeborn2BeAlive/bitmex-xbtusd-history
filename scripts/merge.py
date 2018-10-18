import argparse
from datetime import datetime, timezone, timedelta
import pandas as pd
import json
import os

from utils import timedeltas


def parse_cl_args():
    parser = argparse.ArgumentParser(
        description='Merge multiple scrap file into one big json')
    parser.add_argument(
        'path', help='Path a directory containing the scrapped database (folder 1d, 1h, etc)'
    )
    parser.add_argument(
        'outfile', help='Path to output json file'
    )
    return parser.parse_args()


def load_buckets(path_to_history, timeframe):
    path_to_folder = os.path.join(path_to_history, timeframe)
    buckets = []
    for filename in os.listdir(path_to_folder):
        with open(os.path.join(path_to_folder, filename)) as f:
            data = json.load(f)
            del data['timeframe']
            del data['openDate']
            buckets.append(data)

    return buckets


args = parse_cl_args()

obj = {}
for k in timedeltas.keys():
    print("Loading buckets for timeframe {}".format(k))
    obj[k] = load_buckets(args.path, k)

print("Writing output file")
with open(args.outfile, 'w') as f:
    json.dump(obj, f, indent=2)
