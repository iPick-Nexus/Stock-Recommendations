import time 
import yfinance as yf
import pandas as pd
import pyarrow as pa 
import psycopg2


# Every time run, reads the stock list
#   (nyse-listed.csv)
nyse_listing = pd.read_csv("nyse-listed.csv")

test_df_A = yf.download("A", period = 'max', interval='1d')

# Check whether that stock data is cached and
#   up to date.
#    1) An assumption to make cache-checking 
#       more efficient: for each ticker, if a
#       date exists for that ticker, then we assume
#       the price information is complete and
#       correct.
# Try pulling newest information added to the 
#   existing data (yfinance), explicitly logging 
#   the process and recording any error encountered.
#    1) Any "." character should be
#       replaced with "-" according to yfinance
#       format.
#    2) Try to batch up the requests as much as
#       possible because one bulk request costs less
#       than individual requests.
#    3) What should be the logging format??
#    4) To comply with the assumptions, inspect 
#       the pulled stock data after pulling--any 
#       missing dates, null values, etc. Below are
#       a few issues I can think of:
#        a) A relatively newly listed ticker 
#           such as SPCX. Those stocks may have
#           lots of null values before listing, 
#           and their suitability for training 
#           is questionable.
#        b) A delisted stock?? Not sure if any
#           is contained in the current csv--but
#           we should probably consider checking
#           whether stocks in the list are delisted, 
#           and perhaps dedicate a dataset to 
#           the delisted tickers to address 
#           survivorship bias in the training 
#           process.
#    5) Add/append the new data to the database if
#       above steps are successful without concerns.
# 