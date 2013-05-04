import time
import math
import sys
import TaLib
import json
import websocket
import urllib2
import socket

interval = 1*60     #interval period in seconds
BTCCHARTS_URL = "http://api.bitcoincharts.com/v1/trades.csv?symbol=mtgoxUSD"
MTGOX_SOCKET = "wss://websocket.mtgox.com/mtgox?Currency=USD"
TIMEOUT=10

class IntervalList:
    def __init__(self):
        self.intList = []
        self.sma = MovingAverage(5)
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
    def printIntervalAt(self, n):
        self.intList[n].printInterval()
        print "SMA: %.6g" % (self.sma.compute(self.closings()))
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
    def __init__(self, tradeData):
        self.time = int(tradeData[0]) #unix time
        self.price = float(tradeData[1])
        self.volume = float(tradeData[2])
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

def connect_mtgox():
    print "Connecting to MtGox websocket..."
    sock = websocket.create_connection(MTGOX_SOCKET, TIMEOUT)
    print "Connected!"
    subscribe_cmd = "{'op':'mtgox.subscribe', 'type':'lag'}"
    sock.send(subscribe_cmd)
    sock.recv()
    return sock 
    
def get_mtgoxdata(sock):
    try:
        data = json.loads(sock.recv())
    except socket.timeout:
        print "Timed out. Retrying"
        return None
    return data

intList = IntervalList()

if (False): ##placeholder for cmdline parameter
    start_data = urllib2.urlopen(BTCCHARTS_URL)
    for line in reversed(start_data.readlines()):
        curTrade = Trade(tuple(line.split(",")))
        curTrade.printTrade()
        if intList.empty() or curTrade.intervalID != curInterval.intervalID:
            curInterval = Interval(curTrade)
            if not intList.empty():
                intList.printIntervalAt(-1)
            intList.addInterval(curInterval)
        else:
            curInterval.addTrade(curTrade)
    
mtgox = connect_mtgox()

while True:
    try:
        mtdata = get_mtgoxdata(mtgox)
    except Exception, e:
        print e
        continue

    if (mtdata['channel'] == "dbf1dee9-4f2e-4a08-8cb7-748919a71b21") and (mtdata['trade']['price_currency'] == "USD"):
        mtTrade = mtdata['trade']
        curTrade = Trade((mtTrade['date'], mtTrade['price'], mtTrade['amount']))
        curTrade.printTrade()
        if intList.empty() or curTrade.intervalID != curInterval.intervalID:
            curInterval = Interval(curTrade)
            if not intList.empty():
                intList.printIntervalAt(-1)
            intList.addInterval(curInterval)
        else:
            curInterval.addTrade(curTrade)


