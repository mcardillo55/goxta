"""goxta -- realtime technical analysis on mtGox trading"""
from indicators import *
from goxapi import *
import strategy
import numpy as np
import argparse
import time
import math
import sys
import urllib2
import thread

BTCCHARTS_URL = "http://api.bitcoincharts.com/v1/trades.csv?symbol=mtgoxUSD"


class IntervalList:
    """Main data structure containing all Interval objects

    If trading indicators are desired, they should be passed to the
    'indicators' argument as a list of objects during the IntervalList
    instantiation call

    e.g. newList = IntervalList(indicators=(RSI()))
    """
    def __init__(self, intervalPeriod=1, indicators=()):
        self.intervalPeriod = intervalPeriod * 60  # interval period in secs
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
        """Returns a numpy array of all interval closing prices

        Used by several indicators in indicators.py
        """
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
        indStr = ""
        for curInd in self.indicators:
            indStr = indStr + curInd.asStr(closings) + "\t"
        print indStr


class Interval:
    """Basic trade period unit

    Contains essential trade prices, as well as all Trade objects that took
    place during the interval interval

    empty is passed True if we are creating an interval with no trading
    activity
    open is either the opening trade, or the previous Interval if there is
    no activity
    """
    def __init__(self, open, empty=False):
        if (empty):
            self.intervalID = open.intervalID + 1
            self.open = open.close
            self.close = open.close
            self.trades = []
            self.high = open.close
            self.low = open.close
            self.volume = 0
        else:
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
        print ("ID: %d\tOpen: %.6g\tClose: %.6g\tHigh: %.6g\t"
               "Low: %.6g\tVol: %.6g") % (self.intervalID, self.open,
               self.close, self.high, self.low, self.volume)

    def printTrades(self):
        for trade in self.trades:
            trade.printTrade()


class Trade:
    """Object to contain all essential data about a specific trade"""
    def __init__(self, (tradeData), intervalPeriod):
        # time is unix epoch time
        self.time = int(tradeData[0])
        self.price = float(tradeData[1])
        self.volume = float(tradeData[2])
        self.intervalID = int(math.floor(self.time / intervalPeriod))

    def printTrade(self):
        print "Time: %s\tPrice: %f\tVolume: %f" % (time.ctime(self.time),
                                                self.price, self.volume)

parser = argparse.ArgumentParser(description="Analyze and trade Bitcoin"
                                             "on mtGox")
parser.add_argument("--hist", dest="history", action="store_true",
                    help="Grab recent bitcoincharts.com trade history")
args = parser.parse_args()

# creating main interval list object
intList = IntervalList(indicators=(MovingAverage(10), MovingAverage(20),
                       RSI(), MACD()))

if (args.history):
    print "Fetching history from bitcoincharts.com..."
    start_data = urllib2.urlopen(BTCCHARTS_URL)
    for line in reversed(start_data.readlines()):
        curTrade = Trade(tuple(line.split(",")), intList.getIntervalPeriod())
        if intList.empty() or curTrade.intervalID != curInterval.intervalID:
            curInterval = Interval(curTrade)
            intList.addInterval(curInterval)
        else:
            curInterval.addTrade(curTrade)
    print "Complete!"

mtgox = GoxAPI()
mtgox.connect()

mtgoxThread = GoxAPI()
mtgoxThread.connect()

tradeStrategy = strategy.Strategy()

#thread.start_new_thread(tradeStrategy.run, (mtgoxThread, ))

while True:
    """Main program loop

    Will keep recieving trade data until process dies
    """
    try:
        mtdata = mtgox.getTrades()
    except KeyboardInterrupt:
        print "Received Ctrl+C. Closing goxta..."
        sys.exit(0)
    except ssl.SSLError:
        continue
    except:
        continue

    try:
        # this is the 'trades' channel identifier, according to API docs
        if (mtdata['channel'] == "dbf1dee9-4f2e-4a08-8cb7-748919a71b21" and
           mtdata['trade']['price_currency'] == "USD"):
            mtTrade = mtdata['trade']
        else:
            mtTrade = None
    except:
        continue

    if (mtTrade):
        curTrade = Trade((mtTrade['date'], mtTrade['price'],
                            mtTrade['amount']), intList.getIntervalPeriod())
        # checking if we should create the first Interval in the list or
        # if the trade time has passed the the interval end time, in
        # which we will need to need to create a new Interval
        if (intList.empty() or
           curTrade.intervalID != curInterval.intervalID):
            curInterval = Interval(curTrade)
            # checking for the case in which we need to create the
            # first Interval for the list
            if not intList.empty():
                intList.printIntervalAt(-1)
                idDiff = (curInterval.intervalID -
                         intList.intList[-1].intervalID)
                if (idDiff != 1):
                    for x in range(1, idDiff):
                        intList.addInterval(Interval(intList.intList[-1],
                                            True))
                        intList.printIntervalAt(-1)
            intList.addInterval(curInterval)
        else:
            curInterval.addTrade(curTrade)
        curTrade.printTrade()
