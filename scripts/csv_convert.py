import argparse
from datetime import datetime, timezone, timedelta
import pandas as pd
import json
import os

from utils import timedeltas


def parse_cl_args():
    parser = argparse.ArgumentParser(description='c2ba crypto scraper')
    parser.add_argument(
        'timeframe_database', help='Path a folder containing json files for a specific timeframe (eg. "../1m")'
    )
    parser.add_argument(
        'output_file', help='Path to csv file'
    )
    parser.add_argument(
        '--date', help='If specified, output date as string instead of timestamp and the label becomes "date" instead of "timestamp" in csv file',
        action='store_const', const=True, default=False
    )
    return parser.parse_args()


args = parse_cl_args()

data_dict = {
    'close': [],
    'open': [],
    'high': [],
    'volume': []
}
index = []

for filename in os.listdir(args.timeframe_database):
    df = pd.DataFrame({'close': [], 'open': [], 'high': [],
                       'low': [], 'volume': []}, index=[])
    with open(os.path.join(args.timeframe_database, filename)) as f:
        d = json.load(f)
        open_time = datetime.utcfromtimestamp(d['openTimestamp'])
        tf = d['timeframe']
        if args.date:
            index += [open_time + i * timedeltas[tf]
                      for i in range(len(d['open']))]
        else:
            index += [int((open_time + i * timedeltas[tf] - datetime(1970, 1, 1, 0, 0, 0)).total_seconds())
                      for i in range(len(d['open']))]
        for k in data_dict:
            data_dict[k] += d[k]

df = pd.DataFrame(data_dict, index=index)
df.to_csv(args.output_file, index_label='index' if not args.date else 'date')
