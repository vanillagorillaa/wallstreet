
import csv
import pandas as pd

from datetime import date, timedelta, datetime
from wallstreet import Stock, Call, Put

# Params for options selection

#capital
capital = 5000
contracts = 1
pps_capital = capital / (contracts * 100)

# Greeks
long_delta_min = 0.75
long_delta_max = 0.85
short_delta_min = 0.25
short_delta_max = 0.35
min_volume = 5
min_open_interest = 50


# Times
leap_leg_min = 345
leap_leg_max = 385
short_leg_min = 30
short_leg_max = 45

# IV
_30_day_average = 30
_60_day_average = 60
_120_day_average = 120

# Parsing symbols of stock on NASDAQ
symbols = []
# open file for reading
with open('companies.csv') as csvDataFile:
    # open file as csv file
    csvReader = csv.reader(csvDataFile)
    next(csvReader)
    # loop over rows
    for row in csvReader:
        # add cell [0] to list of dates
        symbols.append(row[0])

# functions
def get_strikes(e):
    strikes = []
    e = e.split("-")
    s = Call(symbol, int(e[1]), int(e[0]), int(e[2]))
    strikes = s.strikes
    return strikes

def get_expirations():
    expirations = []
    try:
        c = Call(symbol)
        try:
            s = Stock(symbol)
            expirations = c.expirations
            return expirations
        except Exception as e:
            pass
    except Exception as e:
        pass

def get_greeks(c):
    greeks = [c.delta(), c.implied_volatility(), c.gamma(), c.theta(), c.vega(), c.rho(), c.volume, c.open_interest]
    return greeks

def get_price(c):
    price = [c.price]
    return price

def get_short_leg():
    parsed_dates = []
    expirations = get_expirations()
    if expirations == None:
        return
    min_date = date + timedelta(days=short_leg_min)
    max_date = date + timedelta(days=short_leg_max)
    min_date = min_date.strftime("%m-%d-%Y")
    max_date = max_date.strftime("%m-%d-%Y")
    for expiration in expirations:
        if compare_dates(min_date,expiration) and compare_dates(expiration,max_date):
            parsed_dates.append(expiration)
    if len(parsed_dates) == 0:
        return
    best_options = []
    for date1 in parsed_dates:
        strikes = get_strikes(date1)
        for strike in strikes:
            e = date1.split("-")
            greeks = get_greeks(Call(symbol, int(e[1]), int(e[0]), int(e[2]), strike))
            if greeks[0] <= short_delta_max and greeks[0] >= short_delta_min and greeks[6] >= min_volume and greeks[7] >= min_open_interest:
                best_options.append([date1, strike, greeks])
    if len(best_options) > 0:
        print("Potential good short picks -- Ticker", symbol, "--" , best_options)

def get_long_leg():
    parsed_dates = []
    expirations = get_expirations()
    if expirations == None:
        return
    min_date = date + timedelta(days=leap_leg_min)
    max_date = date + timedelta(days=leap_leg_max)
    min_date = min_date.strftime("%m-%d-%Y")
    max_date = max_date.strftime("%m-%d-%Y")
    for expiration in expirations:
        if compare_dates(min_date,expiration) and compare_dates(expiration,max_date):
            parsed_dates.append(expiration)
    if len(parsed_dates) == 0:
        return
    best_options = []
    for date1 in parsed_dates:
        strikes = get_strikes(date1)
        for strike in strikes:
            e = date1.split("-")
            price = get_price(Call(symbol, int(e[1]), int(e[0]), int(e[2]), strike))
            if price[0] > pps_capital:
                return
            greeks = get_greeks(Call(symbol, int(e[1]), int(e[0]), int(e[2]), strike))
            if greeks[0] <= long_delta_max and greeks[0] >= long_delta_min:
                best_options.append([date1, strike, greeks])
    if len(best_options) > 0:
        print("Potential good long picks -- Ticker", symbol, "----" , best_options)

def historical_data():
    _30_MDA = []
    _90_MDA = []
    _120_MDA = []
    s = Stock(symbol)
    df = s.historical(days_back=1000, frequency='d')

    print(df)
    print(_30_MDA)
    print(_90_MDA)
    print(_120_MDA)

def compare_dates(d1,d2):
    d1=d1.split('-')  #assuming d1 is min
    d2=d2.split('-')  #assuming d2 is expr

    if d2[2]==d1[2]:
        if d2[0]>d1[0]:
            return True
        elif d2[0]==d1[0]:
            if d2[1]>=d1[1]:
                return True
            else:
                return False
        else:
            return False
    elif d2[2]>d1[2]:
        return True
    else:
        return False

if __name__ == "__main__":
    date = date.today()
    for symbol in symbols:
        #get_short_leg()
        #get_long_leg()
        historical_data()
