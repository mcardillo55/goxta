"""
Common calls to the MtGox API

See https://en.bitcoin.it/wiki/MtGox/API for a more detailed explanation.
"""
import json
import websocket
import time
import hashlib
import hmac
import base64

MTGOX_SOCKET = "wss://websocket.mtgox.com/mtgox?Currency=USD"
TIMEOUT = 10


class GoxAPI():
    def __init__(self):
        self.socket = None
        keydata = open("keydata.conf", "r")
        keyjson = json.loads(keydata.read())
        self.key = keyjson['key']
        self.secret = keyjson['secret']
        keydata.close()

    def connect(self):
        """Opens a connection to mtGox websocket"""
        print "Connecting to MtGox websocket..."
        sock = websocket.create_connection(MTGOX_SOCKET, TIMEOUT)
        print "Connected!"
        subscribe_cmd = "{'op':'mtgox.subscribe', 'type':'lag'}"
        sock.send(subscribe_cmd)
        sock.recv()
        self.socket = sock
        return sock

    def getNonce(self):
        """Generates a unique identifier used when placing orders"""
        return str(time.time())

    def getTrades(self):
        """Attempts to get trades from open mtGox websocket"""
        if self.socket is not None:
            try:
                data = json.loads(self.socket.recv())
            except Exception, e:
                print e
                return None
            return data
        else:
            print "Error: Not connected to mtGox socket"
            return None

    def buy(self, price, vol):
        """Executes a buy order

        price in dollars as float
        volume in btc as float

        Returns order ID (oid) if successful, False if failed
        """
        price = int(price * 1E5)
        vol = int(vol * 1E8)
        params = {
            "type": "bid",
            "amount_int": vol,
            "price_int": price}
        return self.sendSignedCall("order/add", params)

    def sell(self, price, vol):
        """Executes a sell order

        price in dollars as float
        volume in btc as float

        Returns order ID (oid) if successful, False if failed
        """
        price = int(price * 1E5)
        vol = int(vol * 1E8)
        params = {
            "type": "ask",
            "amount_int": vol,
            "price_int": price}
        return self.sendSignedCall("order/add", params)

    def cancel(self, oid):
        """Cancels the order refered by oid"""
        params = {
            "oid": oid}
        return self.sendSignedCall("order/cancel", params)

    def sendSignedCall(self, api, params=None):
        """Packages required mtGox API data and sends the command

        This is a generic function used by both buy and sell commands

        It will return whatever result is specified by the mtGox API if
        successful, or False if the call failed
        """
        nonce = self.getNonce()
        reqId = hashlib.md5(nonce).hexdigest()

        req = json.dumps({
            "id": reqId,
            "call": api,
            "nonce": nonce,
            "params": params,
            "currency": "USD",
            "item": "BTC"})

        signedReq = hmac.new(base64.b64decode(self.secret), req,
                             hashlib.sha512).digest()
        signedAndEncodedCall = base64.b64encode(self.key.replace("-", "")
                                     .decode("hex") + signedReq + req)
        call = json.dumps({
            "op": "call",
            "call": signedAndEncodedCall,
            "id": reqId,
            "context": "mtgox.com"})

        self.socket.send(call)

        while True:
            result = json.loads(self.socket.recv())
            try:
                if (result["id"] == reqId):
                    try:
                        if (result["success"] is False):
                            return False
                    except Exception, e:
                        return result["result"]
            except Exception, e:
                continue
