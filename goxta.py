import time
import math
import sys
import TaLib

class Interval:
    def __init__(self, open):
        self.name = time.ctime(open.time)
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
    def printTrade(self):
        print "Time: %s\tPrice: %f\tVolume: %f" % (time.ctime(self.time), self.price, self.volume)

interval = 1
tradeData = open('data')

def TA_pad_zeros(argvs):
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

def printIntClosing(inter, n):
    print "INTERVAL: " + str(n)
    sma = TA_pad_zeros(TaLib.TA_MA(0,n-1,closings(intervalList,0,n),50))
    print "H: %f\tL: %f\tO: %f\tC: %f\t SMA: %f" % (inter.high, inter.low, inter.open, inter.close, sma[-1])
    #print sma
#    inter.printTrades() 

def closings(intlist, start, end):
    ret = []
    for inter in intlist[start:end]:
        ret.append(inter.close)
    return ret

intervalList = [] 

n=0
for dataLine in tradeData:
    curTrade = Trade(dataLine)
    tradeTime = time.gmtime(curTrade.time)
    hour = getattr(tradeTime, 'tm_hour')
    min = getattr(tradeTime, 'tm_min')
    curInterval = math.floor(min/interval)
    #print "%d %d" % (min, curInterval)

    if  intervalList == [] or oldInterval != curInterval:
        if intervalList != []:
            n+=1
            printIntClosing(intervalGroup, n)
        intervalGroup = Interval(curTrade)
        intervalList.append(intervalGroup)
    else:
        intervalGroup.addTrade(curTrade)

    oldInterval=curInterval


