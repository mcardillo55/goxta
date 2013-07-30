"""Initializations and definitions of technical indicators

These are basically a wrapper around the TA-Lib functions, tailored to be
used by goxta. Feel free to add additional indicators.

See talib.pyx in the talib Python wrapper (https://github.com/mrjbq7/ta-lib)
to view the function headers for your desired indicator.
"""
import talib


class Indicator:
    """Skeleton class for all Indicators

    All indicators must redefine the functions in this class
    """
    def compute(self, closeList):
        raise NotImplementedError

    def display(self, closeList):
        raise NotImplementedError

    def asStr(self, closeList):
        raise NotImplementedError


class SMA(Indicator):
    def __init__(self, t=10):
        self.period = t
        self.last = float('nan')

    def compute(self, closeList):
        self.last = talib.SMA(closeList, self.period)[-1]
        return self.last

    def display(self, closeList):
        print "SMA(%d): %.6g" % (self.period, self.compute(closeList))

    def asStr(self, closeList):
        return "SMA(%d): %.6g" % (self.period, self.compute(closeList))

class EMA(Indicator):
    def __init__(self, t=10):
        self.period = t
        self.last = float('nan')

    def compute(self, closeList):
        self.last = talib.EMA(closeList, self.period)[-1]
        return self.last

    def display(self, closeList):
        print "EMA(%d): %.6g" % (self.period, self.compute(closeList))

    def asStr(self, closeList):
        return "EMA(%d): %.6g" % (self.period, self.compute(closeList))

class RSI(Indicator):
    def __init__(self, t=14):
        self.period = t
        self.last = float('nan')

    def compute(self, closeList):
        self.last = talib.RSI(closeList, self.period)[-1]
        return self.last

    def display(self, closeList):
        print "RSI(%d): %.6g" % (self.period, self.compute(closeList))

    def asStr(self, closeList):
        return "RSI(%d): %.6g" % (self.period, self.compute(closeList))


class MACD(Indicator):
    def __init__(self, shortt=12, longt=26, sigt=9):
        self.shortt = shortt
        self.longt = longt
        self.sigt = sigt
        self.last = float('nan')

    def compute(self, closeList):
        macd = talib.MACD(closeList, fastperiod=self.shortt,
                          slowperiod=self.longt, signalperiod=self.sigt)
        self.last = (macd[0][-1], macd[1][-1], macd[2][-1])
        return self.last

    def display(self, closeList):
        print "MACD(%d, %d): %.6g, %.6g, %.6g" % ((self.longt, self.shortt)
                + self.compute(closeList))

    def asStr(self, closeList):
        return "MACD(%d, %d): %.6g, %.6g, %.6g" % ((self.longt, self.shortt)
                + self.compute(closeList))
