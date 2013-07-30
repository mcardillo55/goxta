import time
import math


class Strategy:
    def __init__(self, intList):
        self.intList = intList
        self.indicators = intList.indicators

    def addRule(self):
        return

    def removeRule(self):
        return

    def run(self, mtgox):
        #dumb test thread
        while (1):
            oid1 = False
            oid2 = False
            time.sleep(2)
            print "Strategy: Biding on some bitcoins!"
            while (not oid1):
                oid1 = mtgox.buy(30, 0.02)
            time.sleep(2)
            print "Strategy: Selling some bitcoins!"
            while (not oid2):
                oid2 = mtgox.sell(1000, 0.02)
            time.sleep(2)
            print "Strategy: CANCELING ORDERS!"
            while(not mtgox.cancel(oid1)):
                continue
            while(not mtgox.cancel(oid2)):
                continue
