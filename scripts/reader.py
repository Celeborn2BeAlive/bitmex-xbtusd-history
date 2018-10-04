import argparse
from datetime import datetime, timezone, timedelta
import pandas as pd
import json
import os


def parse_cl_args():
    parser = argparse.ArgumentParser(description='c2ba crypto scraper')
    parser.add_argument(
        'jsonfile', help='Path to a json file containing OHLCV candles'
    )
    return parser.parse_args()


timedeltas = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1)
}

args = parse_cl_args()

with open(args.jsonfile) as f:
    d = json.load(f)
    open_time = datetime.utcfromtimestamp(d['openTimestamp'])
    tf = d['timeframe']
    index = [open_time + i * timedeltas[tf] for i in range(len(d['open']))]
    df = pd.DataFrame({'close': d['close'], 'open': d['open'], 'high': d['high'],
                       'low': d['low'], 'volume': d['volume']}, index=index)
    print(df)
    print(df.describe())
