goxta
=====

The goal of goxta is to create a realtime MtGox trading platform that will support a variety of technical indicators which can be used in a personal automated trading strategy.

Dependencies
------------
* TA-Lib python wrapper - available at http://mrjbq7.github.io/ta-lib/

* A websocket module - I use websocket-client, available on PyPI

Configuration
-------------
For now, an MtGox API key is required to be placed in a file in the same directory called "keydata.conf". The format should be in JSON as follows:

`{ "key" : "YOUR KEY HERE", "secret" : "YOUR SECRET HERE" }`

