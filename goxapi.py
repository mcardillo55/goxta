import json
import websocket
import time
import hashlib
import hmac
import base64

MTGOX_SOCKET = "wss://websocket.mtgox.com/mtgox?Currency=USD"
TIMEOUT=10

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
