import time
import math
import sys
import TaLib

class IntervalList:
    def __init__(self):
        self.intList = []
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
        return closeList
    def printFullList(self):
        for interval in self.intList:
            print "INTERVAL ID: %d" % interval.intervalID
            interval.printTrades()

class Interval:
    def __init__(self, open):
        self.intervalID = open.intervalID
        self.open = open.price
        self.close = open.price
        self.trades = [open]
        self.high = open.price
        self.low = open.price
    def printTrades(self):
        for trade in self.trades:
            trade.printTrade()
    def addTrade(self, trade):
        self.trades.append(trade)
        self.close = trade.price
        if trade.price > self.high:
            self.high = trade.price
        if trade.price < self.low:
            self.low = trade.price

class Trade:
    def __init__(self, tradeData):
        splitData = tradeData.split(',')
        self.time = int(splitData[0]) #unix time
        self.price = float(splitData[1])
        self.volume = float(splitData[2])
        self.intervalID = int(math.floor(self.time/interval))
    def printTrade(self):
        print "Time: %s\tPrice: %f\tVolume: %f" % (time.ctime(self.time), self.price, self.volume)

class Indicator:
    def compute(self):
        raise NotImplementedError

    def TA_pad_zeros(self, argvs):
        end = argvs[1]
        try:
            seq = argvs[2]
        except:
            seq = [0,0]
        end = int(end)
        nseq = []
        for x in range(end):
            nseq.append(0)
        for x in seq:
            nseq.append(x)
        return nseq

class MovingAverage(Indicator):
    def __init__(self, t=10):
        self.period = t
    def compute(self, closeList):
        return self.TA_pad_zeros(TaLib.TA_MA(0, len(closeList)-1, closeList, self.period))[-1]

interval = 5*60     #in seconds
tradeData = open('data')
intList = IntervalList()

for dataLine in tradeData:
    curTrade = Trade(dataLine)

    if intList.empty() or curTrade.intervalID != curInterval.intervalID:
        curInterval = Interval(curTrade)
        intList.addInterval(curInterval)
    else:
        curInterval.addTrade(curTrade)
