#! /usr/bin/env python3
# coding: utf-8

import socket
import sys
import zmq
# import signal
# import json
from ezproxy import EmacsProxy, BrokerProxy, FROM


def main():
    emacs = EmacsProxy(FROM) \
            .connect()       \
            .shakeHands()
    print("Initialized EmacsProxy")
    broker = BrokerProxy()   \
             .connect()
    print("Initialized BrokerProxy")
    while True:
        # TODO:
        messageMap = emacs.receive()
        broker.send(messageMap)


if __name__ == "__main__":
    main()


#  LocalWords:  usr utf BrokerProxy
