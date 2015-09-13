#! /usr/bin/env python3
# coding: utf-8

import socket
import sys
import zmq
# import signal
# import json
from ezproxy import EmacsProxy, BrokerProxy, TO


def main():
    emacs = EmacsProxy(TO) \
            .connect()     \
            .shakeHands()
    print("Initialized EmacsProxy")
    broker = BrokerProxy() \
             .connect()
    print("Initialized BrokerProxy")
    while True:
        # TODO:
        messageMap = broker.receive()
        emacs.send(messageMap)


if __name__ == "__main__":
    main()


#  LocalWords:  utf usr EmacsProxy BrokerProxy
