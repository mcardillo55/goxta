import time
import math
import sys
import TaLib
import json
import websocket
import urllib2
import socket
import hashlib
import hmac
import base64

BTCCHARTS_URL = "http://api.bitcoincharts.com/v1/trades.csv?symbol=mtgoxUSD"
MTGOX_SOCKET = "wss://websocket.mtgox.com/mtgox?Currency=USD"
TIMEOUT=10

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
        return closeList
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

class Indicator:
    def compute(self, closeList):
        raise NotImplementedError
    def display(self, closeList):
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
    def __init__(self, t=50):
        self.period = t
    def compute(self, closeList):
        return self.TA_pad_zeros(TaLib.TA_MA(0, len(closeList)-1, closeList, self.period))[-1]
    def display(self, closeList):
        print "SMA: %.6g" % (self.compute(closeList))

class RSI(Indicator):
    def __init__(self, t=14):
        self.period = t
    def compute(self, closeList):
        return self.TA_pad_zeros(TaLib.TA_RSI(0, len(closeList)-1, closeList, self.period))[-1]
    def display(self, closeList):
        print "RSI: %.6g" % (self.compute(closeList))


class MACD(Indicator):
    def __init__(self, shortt=12, longt=26, sigt=9):
        self.shortt = shortt
        self.longt = longt
        self.sigt = sigt
    def compute(self, closeList):
        return self.TA_pad_zeros(TaLib.TA_MACD(0, len(closeList)-1, closeList, self.shortt, \
                    self.longt, self.sigt))[-1]
    def display(self, closeList):
        print "MACD: %.6g" % self.compute(closeList)

class GoxAPI():
    def __init__(self):
        self.socket = None
        keydata = open("keydata.conf", "r")
        keyjson = json.loads(keydata.read())
        self.key = keyjson['key']
        self.secret = keyjson['secret']
        keydata.close()
    def connect(self):
        print "Connecting to MtGox websocket..."
        sock = websocket.create_connection(MTGOX_SOCKET, TIMEOUT)
        print "Connected!"
        subscribe_cmd = "{'op':'mtgox.subscribe', 'type':'lag'}"
        sock.send(subscribe_cmd)
        sock.recv()
        self.socket = sock
        return sock 
    def getNonce(self):
        return str(time.time())
    def getTrades(self):
        if self.socket is not None:
            try:
                data = json.loads(self.socket.recv())
            except socket.timeout:
                print "Timed out. Retrying"
                return None
            return data
        else:
            print "Error: Not connected to mtGox socket"
            return None
    def buy (self, price, vol):
        price = int(price * 1E5)
        vol = int(vol * 1E8)
        params = {
            "type"      : "bid",
            "amount_int": vol,
            "price_int" : price}
        self.sendSignedCall("order/add", params)
    def sell(self, price, vol):
        price = int(price * 1E5)
        vol = int(vol * 1E8)
        params = {
            "type"      : "ask",
            "amount_int": vol,
            "price_int" : price}
        self.sendSignedCall("order/add", params)
    def cancel(self, oid):
        params = {
            "oid"       : oid}
        self.sendSignedCall("order/cancel", params)
    def sendSignedCall(self, api, params):
        nonce = self.getNonce()
        reqId = hashlib.md5(nonce).hexdigest()

        req = json.dumps({
            "id"        : reqId,
            "call"      : api,
            "nonce"     : nonce,
            "params"    : params,
            "currency"  : "USD",
            "item"      : "BTC"})
         
        signedReq = hmac.new(base64.b64decode(self.secret), req, hashlib.sha512).digest()
        signedAndEncodedCall = base64.b64encode(self.key.replace("-","").decode("hex")  + signedReq + req)
        call = json.dumps({
            "op"        : "call",
            "call"      : signedAndEncodedCall,
            "id"        : reqId,
            "context"   : "mtgox.com"})

        self.socket.send(call)

intList = IntervalList(indicators=(MovingAverage(), RSI(), MACD()))

if (True): ##placeholder for cmdline parameter
    print "Fetching history from bitcoincharts.com..."
    start_data = urllib2.urlopen(BTCCHARTS_URL)
    for line in reversed(start_data.readlines()):
        curTrade = Trade(tuple(line.split(",")), intList.getIntervalPeriod())
        #curTrade.printTrade()
        if intList.empty() or curTrade.intervalID != curInterval.intervalID:
            curInterval = Interval(curTrade)
            if not intList.empty():
                intList.printIntervalAt(-1)
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


