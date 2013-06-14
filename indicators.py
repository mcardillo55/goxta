import talib

class Indicator:
    def compute(self, closeList):
        raise NotImplementedError
    def display(self, closeList):
        raise NotImplementedError

class MovingAverage(Indicator):
    def __init__(self, t=50):
        self.period = t
    def compute(self, closeList):
        return talib.SMA(closeList, self.period)[-1]
    def display(self, closeList):
        print "SMA: %.6g" % (self.compute(closeList))

class RSI(Indicator):
    def __init__(self, t=14):
        self.period = t
    def compute(self, closeList):
        return talib.RSI(closeList, self.period)[-1]
    def display(self, closeList):
        print "RSI: %.6g" % (self.compute(closeList))


class MACD(Indicator):
    def __init__(self, shortt=12, longt=26, sigt=9):
        self.shortt = shortt
        self.longt = longt
        self.sigt = sigt
    def compute(self, closeList):
        macd = talib.MACD(closeList, fastperiod=self.shortt, slowperiod=self.longt, signalperiod=self.sigt)
        return (macd[0][-1], macd[1][-1], macd[2][-1])
    def display(self, closeList):
        print "MACD: %.6g, %.6g, %.6g" % self.compute(closeList)

