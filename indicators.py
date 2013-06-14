import TaLib
import talib

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
        return talib.SMA(closeList, self.period)[-1]
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


