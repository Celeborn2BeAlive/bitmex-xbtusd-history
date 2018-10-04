import argparse
from datetime import datetime, timezone, timedelta
import pandas as pd
import json
import os
import bitmex
import time


def parse_cl_args():
    parser = argparse.ArgumentParser(description='c2ba crypto scraper')
    parser.add_argument(
        'outfolder', help='Path to output folder, where to store scraped OHLC data'
    )
    return parser.parse_args()


def ensure_mkdir(p):
    if not os.path.exists(p):
        os.mkdir(p)
    else:
        if not os.path.isdir(p):
            raise RuntimeError("{} is not a directory.".format(p))


timedeltas = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1)
}

client = bitmex.bitmex(test=False)


def fetch_ohlcv(tf, limit, since):
    # adding one time interval because this api is returning us close times instead of open times
    closeDate = since + timedeltas[tf]
    result = client.Trade.Trade_getBucketed(
        symbol="XBTUSD", reverse=False, count=limit, binSize=tf, startTime=closeDate).result()[0]

    candles = [candle for candle in result if candle["open"]]

    # compute open and close times of each candle
    for candle in candles:
        candle["openDate"] = candle['timestamp'] - timedeltas[tf]
        candle["closeDate"] = candle['timestamp']

    return candles


def store_dict(tf, current_out_file, current_dict):
    if not current_out_file:
        return
    current_out_filename = os.path.join(
        args.outfolder, tf, current_out_file)
    with open(current_out_filename, 'w') as f:
        json.dump(current_dict, f)


args = parse_cl_args()

ensure_mkdir(args.outfolder)
for tf in timedeltas.keys():
    ensure_mkdir(os.path.join(args.outfolder, tf))

limit = 750  # max number of candles that bitmex is sending


def get_out_file(candle, tf):
    openDate = candle["openDate"]
    if tf == '1d':  # group by month
        month_date = datetime(openDate.year, openDate.month, 1)
        return month_date.strftime("XBTUSD-%Y-%m-%d-{}.json".format(tf))

    if tf == '1h':  # group by week
        week_date = openDate - timedelta(days=openDate.weekday())
        return week_date.strftime("XBTUSD-%Y-%m-%d-{}.json".format(tf))

    # group by day
    day_date = datetime(openDate.year, openDate.month, openDate.day)
    return day_date.strftime("XBTUSD-%Y-%m-%d-{}.json".format(tf))


for tf in timedeltas.keys():
    while True:
        time.sleep(2)  # ensure we don't flood bitmex API with requests

        since = datetime(1970, 1, 1, tzinfo=timezone.utc)
        # find the most recent date for which data was gathered:
        for filename in os.listdir(os.path.join(args.outfolder, tf)):
            split = filename.split("-")
            year = int(split[1])
            month = int(split[2])
            day = int(split[3])
            date = datetime(year, month, day, tzinfo=timezone.utc)
            if date >= since:
                since = date

        if since != datetime(1970, 1, 1, tzinfo=timezone.utc):
            filename = os.path.join(args.outfolder, tf, since.strftime(
                "XBTUSD-%Y-%m-%d-{}.json".format(tf)))
            with open(filename) as f:
                d = json.load(f)
                firstdate = datetime.utcfromtimestamp(d["openTimestamp"])
                since = firstdate + len(d["open"]) * timedeltas[tf]

        # fetch data
        print("Fetching ohlcv candles for timeframe {} since {}".format(tf, since))
        result = fetch_ohlcv(tf, limit=limit, since=since)

        print("{} ohlcv candles received.".format(len(result)))

        if len(result) == 0:
            print("No candles received for timeframe {}, work is done.".format(tf))
            break

        current_out_file = None
        current_dict = None

        for candle in result:
            out_file = get_out_file(candle, tf)
            if out_file != current_out_file:
                store_dict(tf, current_out_file, current_dict)

                # open new file
                current_out_file = out_file
                current_out_filename = os.path.join(
                    args.outfolder, tf, current_out_file)
                if os.path.exists(current_out_filename):
                    with open(current_out_filename) as f:
                        current_dict = json.load(f)
                else:
                    current_dict = {
                        "openTimestamp": int(candle["openDate"].timestamp()),
                        "timeframe": tf,
                        "openDate": candle["openDate"].strftime('%Y-%m-%d %H:%M:%S'),
                        "open": [], "high": [], "low": [], "close": [], "volume": [],
                        # "openDate": [], "closeDate": []
                    }

            current_dict["open"].append(candle["open"])
            current_dict["high"].append(candle["high"])
            current_dict["low"].append(candle["low"])
            current_dict["close"].append(candle["close"])
            current_dict["volume"].append(candle["volume"])

            # Not needed since we have the openTimestamp of the first candle and we know the timeframe; keep in comment for debug
            # current_dict["openDate"].append(str(candle["openDate"]))
            # current_dict["closeDate"].append(str(candle["closeDate"]))

        store_dict(tf, current_out_file, current_dict)
