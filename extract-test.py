# Checks possible non-alphabet characters contained in tickers, and check whether yfinance handle them properly.

import pandas as pd

df = pd.read_csv("nyse-listed.csv")

symbols = df["ACT Symbol"].dropna().astype(str)

# Extract every character that is not A-Z or a-z
non_alpha = sorted(set(
    char
    for symbol in symbols
    for char in symbol
    if not char.isalpha()
))

print(non_alpha)

# The possible non-alpha characters are:
# [Awaiting execution]