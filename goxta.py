from indicators import *
from goxapi import *
import numpy as np
import argparse
import time
import math
import sys
import urllib2

BTCCHARTS_URL = "http://api.bitcoincharts.com/v1/trades.csv?symbol=mtgoxUSD"

class IntervalList:
    def __init__(self, intervalPeriod = 1, indicators = ()):
        self.intervalPeriod = intervalPeriod*60     #interval period in seconds
        self.intList = []
        self.indicators = indicators
    def addInterval(self, newInterval):
        self.intList.append(newInterval)
    def empty(self):
        if self.intList == []:
            return True
        else:
            return False
    def closings(self):
        closeList = []
        for interval in self.intList:
           closeList.append(interval.close) 
        return np.array(closeList)
    def getIntervalPeriod(self):
        return self.intervalPeriod
    def printIntervalAt(self, n):
        self.intList[n].printInterval()
        self.printIndicators()
    def printFullList(self):
        for interval in self.intList:
            print "INTERVAL ID: %d" % interval.intervalID
            interval.printTrades()
    def printIndicators(self):
        closings = self.closings()
        for curInd in self.indicators:
            curInd.display(closings)

class Interval:
    def __init__(self, open):
        self.intervalID = open.intervalID
        self.open = open.price
        self.close = open.price
        self.trades = [open]
        self.high = open.price
        self.low = open.price
        self.volume = open.volume
    def addTrade(self, trade):
        self.trades.append(trade)
        self.volume = self.volume + trade.volume
        self.close = trade.price
        if trade.price > self.high:
            self.high = trade.price
        if trade.price < self.low:
            self.low = trade.price
    def printInterval(self):
        print ("ID: %d\tOpen: %.6g\tClose: %.6g\tHigh: %.6g\tLow: %.6g\tVol: %.6g") % \
                (self.intervalID, self.open, self.close, self.high, self.low, self.volume)
    def printTrades(self):
        for trade in self.trades:
            trade.printTrade()

class Trade:
    def __init__(self, (tradeData), intervalPeriod):
        self.time = int(tradeData[0]) #unix time
        self.price = float(tradeData[1])
        self.volume = float(tradeData[2])
        self.intervalID = int(math.floor(self.time/intervalPeriod))
    def printTrade(self):
        print "Time: %s\tPrice: %f\tVolume: %f" % (time.ctime(self.time), self.price, self.volume)

parser = argparse.ArgumentParser(description="Analyze and trade Bitcoin on mtGox")
parser.add_argument("--no-hist", dest="history", action="store_false", help="Disable fetching bitcoincharts.com history")
args = parser.parse_args()

intList = IntervalList(indicators=(MovingAverage(), RSI(), MACD()))

if (args.history):
    print "Fetching history from bitcoincharts.com..."
    start_data = urllib2.urlopen(BTCCHARTS_URL)
    for line in reversed(start_data.readlines()):
        curTrade = Trade(tuple(line.split(",")), intList.getIntervalPeriod())
        #curTrade.printTrade()
        if intList.empty() or curTrade.intervalID != curInterval.intervalID:
            curInterval = Interval(curTrade)
            #if not intList.empty():
                #intList.printIntervalAt(-1)
            intList.addInterval(curInterval)
        else:
            curInterval.addTrade(curTrade)
    print "Complete!"
    
mtgox = GoxAPI()
mtgox.connect()

while True:
    try:
        mtdata = mtgox.getTrades()
    except Exception, e:
        print e
        continue

    try:
        if (mtdata['channel'] == "dbf1dee9-4f2e-4a08-8cb7-748919a71b21") and (mtdata['trade']['price_currency'] == "USD"):
            mtTrade = mtdata['trade']
            curTrade = Trade((mtTrade['date'], mtTrade['price'], mtTrade['amount']), intList.getIntervalPeriod())
            curTrade.printTrade()
            if intList.empty() or curTrade.intervalID != curInterval.intervalID:
                curInterval = Interval(curTrade)
                if not intList.empty():
                    intList.printIntervalAt(-1)
                intList.addInterval(curInterval)
            else:
                curInterval.addTrade(curTrade)
    except Exception, e:
        continue


