# bitmex-xbtusd-history
OHLCV history of XBTUSD bitmex contract, with python scripts to update it.

## Why this repository ?

Bitmex provides through its API a quite long history of OHLCV candles for their XBTUSD contract, which approximately follows the BTC/USD index. Most exhanges only provide recent months of data, even just weeks or days for 1m chars.

I decided to scrap all the data I can from the bitmex API and store it in this repository in case they decide to remove old data.

I also provide a script to keep the data updated, that I periodically run in order to maintain the repository also updated.

## Database structure

At the root of the database we have a folder for each timeframe supported by the bitmex API: 1d, 1h, 5m and 1m. Candles for each timeframe are stored in the corresponding folder, inside json files.

For 1d timeframe, each file contains one month of data. For 1h timeframe, each file contains one week of data. For 5m and 1m timeframes, each file contains one day of data.

Each json file is name with the following pattern: 'XBTUSD-%Y-%m-%d-<TF>.json' where '%Y-%m-%d' is the date of the first day of the data bundle (first day of month for 1d timeframe, first day of week for 1h timeframe, and day of the data for 5m and 1m). '<TD>' is the timeframe.
  
Inside each json file, a json object is stored with the following fields:
- openTimestamp: timestamp in seconds of the first candle of the file (integer, UTC timezone, open time of the candle)
- timeframe: the timeframe of the candles of the file (also in filename and folder name)
- openDate: textual representation '%Y-%m-%d %H:%M:S' of the openTimestamp
- open: array of open prices
- close: array of close prices
- high: array of high prices
- low: array of low prices
- volume: array of volumes

## How to update OHLCV candles

You need python 3 to run the updater.

In 'scripts' directory:

Create the python virtual environment and install required packages to it:
```bash
cd scripts
virtualenv env
source env/Scripts/activate
pip install -r requirements.txt
```

Then the script can be run. It takes a single argument that is the directory where the database is stored. 
```bash
python updater.py ..
```

## Todo

- A script to merge multiple json files
- An interface to read the database as a single entity, without carrying about files
