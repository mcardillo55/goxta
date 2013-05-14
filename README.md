goxta
=====

The goal of goxta is to create a realtime MtGox trading platform that will support a variety of technical indicators which can be used in a personal automated trading strategy.

Dependencies
------------
* TA-Lib -  Available at http://www.ta-lib.org (looking to replace with a ta-lib version with more python support)

  Good SWIG compilation instructions can be found [here](http://blog.mediafederation.com/andy-hawkins/getting-ta-lib-to-work-with-python-2-6-swig-interface/)
* websocket module - I use websocket-client, available on PyPI

Configuration
-------------
For now, an MtGox API key is required to be placed in a file in the same directory called "keydata.conf". The format should be in JSON as follows:

`{ "key" : "YOUR KEY HERE", "secret" : "YOUR SECRET HERE" }`

