#!/usr/bin/env python
"Print stock prices of companies I am interested in"
from yahoo_finance import Share

class StockInfo(object):
    "Information from a stock"
    symbol = ""
    openprice = 0.0
    price = 0.0
    high52week = 0.0
    ave50day = 0.0

    def __init__(self, symbol, openprice, price, high52week, ave50day):
        self.symbol = symbol
        self.openprice = openprice
        self.price = price
        self.high52week = high52week
        self.ave50day = ave50day

def get_stock_info(symbol):
    "Make a stock info object from the symbol"
    stock = Share(symbol)
    stock.refresh()
    info = StockInfo(symbol, stock.get_open(), stock.get_price(), stock.get_year_high(),
                     stock.get_50day_moving_avg())
    return info

def pretty_print_stock_info(stock):
    "Print the stock symbol and price formatted correctly"
    watch = ""
    try:
        ave50day = float(stock.ave50day)
        price = float(stock.price)
        if price < ave50day:
            watch = "X"
        print '{:6s}   {:8.2f}   {:8.2f}   {:8.2f}   {:8.2f}   {:1s}'.format(stock.symbol,
                                                                             float(stock.openprice),
                                                                             float(stock.price),
                                                                             float(stock.ave50day),
                                                                             float(stock.high52week),
                                                                             watch)
    except:
        print '{:6s}   {:>8}   {:>8}   {:>8}   {:>8}   {:>1}'.format(stock.symbol,
                                                                     stock.openprice,
                                                                     stock.price,
                                                                     stock.ave50day,
                                                                     stock.high52week,
                                                                     watch)

def pretty_print_headers():
    "Print the headers in the desired format"
    pretty_print_stock_info(StockInfo("SYMBOL", "OPEN", "PRICE", "YEARHIGH", "50DAYAVE"))
    pretty_print_stock_info(StockInfo("------", "----", "-----", "--------", "--------"))

def get_pretty_print_stock_info(symbol):
    "Get the price for given stock and print it correctly"
    stock = get_stock_info(symbol)
    pretty_print_stock_info(stock)

def get_pretty_print_all_stock_info(symbols):
    "Print stock information for a list of symbols"
    pretty_print_headers()
    for onesymbol in symbols:
        get_pretty_print_stock_info(onesymbol)

def print_my_stocks():
    "Print the stock information for symbols that I am interested in"
    mysymbols = ['AMZN', 'MSFT', 'AAPL', 'SPY', 'PJP', 'XPH', 'VWO',
                 'VNQ', 'QQQ', 'IBB', 'INDY', 'FB', 'BABA', 'VOO', 'XLE']
    get_pretty_print_all_stock_info(mysymbols)
 
print_my_stocks()
