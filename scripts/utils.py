from datetime import datetime, timezone, timedelta
import os
import json

timedeltas = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1)
}


def build_index(database_path):
    for timeframe in timedeltas.keys():
        path_to_folder = os.path.join(database_path, timeframe)
        index = {}
        for filename in os.listdir(path_to_folder):
            with open(os.path.join(path_to_folder, filename)) as f:
                data = json.load(f)
                timestamp = int(data['openTimestamp'])
                count = len(data['open'])
                endTimestamp = int(timestamp + count *
                                   timedeltas[timeframe].total_seconds())
                index[filename] = [timestamp, endTimestamp]
        with open(os.path.join(database_path, '{}-index.json'.format(timeframe)), 'w') as f:
            json.dump(index, f, indent=4)
