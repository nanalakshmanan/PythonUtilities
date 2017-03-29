#!/usr/bin/env python
"Print stock prices of companies I am interested in"
import csv
import datetime
from yahoo_finance import Share

def safe_convert_to_float(value):
    "Convert the value to float. Return 0 if conversion fails"
    try:
        return float(value)
    except:
        return 0.0

def safe_convert_to_datetime(date_as_str):
    "Parse string into a datetime object"
    return datetime.datetime.strptime(date_as_str, "%m/%d/%y")

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

    def pretty_print(self):
        "Print the stock symbol and price formatted correctly"
        watch = ""
        format_str = '{:6s}   {:8.2f}   {:8.2f}   {:8.2f}   {:8.2f}   {:1s}'

        if self.price < self.ave50day:
            watch = "X"

        print format_str.format(self.symbol, self.openprice, self.price, self.ave50day,
                                self.high52week, watch)

    @staticmethod
    def pretty_print_headers():
        "Print the headers in the desired format"
        format_str = '{:>6}   {:>8}   {:>8}   {:>8}   {:>8}'
        print format_str.format("SYMBOL", "OPEN", "PRICE", "50DAYAVE", "YEARHIGH")
        print format_str.format("------", "----", "-----", "--------", "--------")

class StockInfoCache(object):
    "Cache of stock info"
    cache = {}

    def add(self, key, elem):
        "Add an element to the cache"
        self.cache[key] = elem

    def get(self, key):
        "Returns an element from the cache"
        if key in self.cache.keys():
            return self.cache[key]
        else:
            return None

class StockLot(object):
    "Represents one lot of a stock"
    symbol = ""
    purchase_price = 0.0
    purchase_date = safe_convert_to_datetime('01/01/01')
    count = 0
    stock_info = None
    gain = 0.0
    LONG = 1
    SHORT = 2
    stock_type = LONG

    def get_stock_lot_type(self):
        "Determine whether this lot is LONG or SHORT"
        comp_date = datetime.datetime.now() - datetime.timedelta(days=365)
        if self.purchase_date > comp_date:
            return StockLot.SHORT
        else:
            return StockLot.LONG

    def get_stock_lot_type_display(self):
        "String to display based on the type of lot"
        if self.stock_lot_type == StockLot.SHORT:
            return 'SHORT'
        else:
            return 'LONG'

    def __init__(self, symbol, purchase_price, purchase_date, count):
        self.symbol = symbol
        self.stock_info = get_stock_info(symbol)
        self.purchase_date = safe_convert_to_datetime(purchase_date)
        self.purchase_price = purchase_price
        self.count = count
        self.gain = (self.stock_info.price - purchase_price) * self.count
        self.stock_lot_type = self.get_stock_lot_type()

    def calculate_tax(self):
        "Calculates tax for a given lot"
        gross_value = self.count * self.stock_info.price
        tax = 0.0
        if self.stock_lot_type == StockLot.LONG:
            tax = self.gain * 0.2
        else:
            tax = self.gain * 0.4
        net_value = gross_value - tax

        return (tax, gross_value, net_value)

    def pretty_print(self):
        "Pretty print the stock info"

        watch = ""
        stock_lot_type_display = self.get_stock_lot_type_display()

        if self.stock_info.price < self.stock_info.ave50day:
            watch = "X"
        format_str = '{:6s}   {:8.2f}   {:8.2f}   {:8.2f}   {:8.2f}   {:8.2f}   {:8.2f}   {:8.2f}   {:>5}   {:1s}'
        stock_info = self.stock_info
        tax, gross_value, net_value = self.calculate_tax()
        
        print format_str.format(self.symbol, self.purchase_price, stock_info.price,
                                stock_info.ave50day, stock_info.high52week, self.gain,
                                gross_value, net_value,
                                stock_lot_type_display, watch)

    @staticmethod
    def pretty_print_headers():
        "Print the headers in the desired format"
        format_str = '{:>6}   {:>8}   {:>8}   {:>8}   {:>8}   {:>8}   {:>8}   {:>8}   {:>5}'
        print format_str.format("SYMBOL", "PURCHASE", "PRICE", "50DAYAVE",
                                "YEARHIGH", "GAIN", "GROSS", "NET", "TYPE")
        print format_str.format("------", "--------", "-----", "--------",
                                "--------", "-----", "---", "----", "----")

STOCK_INFO_CACHE = StockInfoCache()

def get_stock_info_from_cache(symbol):
    "Return element from cache if available, if not create"
    if STOCK_INFO_CACHE.get(symbol) != None:
        return STOCK_INFO_CACHE.get(symbol)
    stock = Share(symbol)
    stock.refresh()
    STOCK_INFO_CACHE.add(symbol, stock)
    return stock

def get_stock_info(symbol):
    "Make a stock info object from the symbol"
    stock = get_stock_info_from_cache(symbol)
    price = safe_convert_to_float(stock.get_price())
    open_price = safe_convert_to_float(stock.get_open())
    year_high = safe_convert_to_float(stock.get_year_high())
    ave_50day_moving = safe_convert_to_float(stock.get_50day_moving_avg())

    info = StockInfo(symbol, open_price, price, year_high, ave_50day_moving)
    return info

def print_my_stocks():
    "Print the stock information for symbols that I am interested in"
    mysymbols = ['AMZN', 'MSFT', 'AAPL', 'SPY', 'PJP', 'XPH', 'VWO',
                 'VNQ', 'QQQ', 'IBB', 'INDY', 'FB', 'BABA', 'VOO', 'XLE']
    StockInfo.pretty_print_headers()
    stock_info_list = map(get_stock_info, mysymbols)
    for stock_info in stock_info_list:
        stock_info.pretty_print()

def make_stock_lot(row):
    "Make a Stock Info object from a row of csv"
    date = (row[3])
    purchase_price = safe_convert_to_float(row[2])
    count = safe_convert_to_float(row[1])
    return StockLot(row[0], purchase_price, date, count)

def print_csv_data(datafilename):
    "Print contents of a csv file"
    StockLot.pretty_print_headers()
    stock_lot_list = get_stock_lot(datafilename)
    for stock_lot in stock_lot_list:
        stock_lot.pretty_print()

def get_stock_lot(datafilename):
    "Gets a list of stock lot objects from the data file"
    stock_lot_list = []
    with open(datafilename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', dialect=csv.excel)
        for row in reader:
            stock_lot = make_stock_lot(row)
            stock_lot_list.append(stock_lot)
    return stock_lot_list

def print_my_csv():
    "Print the details of csv file of interest"
    print_csv_data("Data.csv")

print_my_csv()
#print_my_stocks()
