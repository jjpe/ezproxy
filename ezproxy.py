#! /usr/bin/env python3
# coding: utf-8

import socket
import sys
import zmq
import json


TO_BROKER_ADDRESS =   'tcp://127.0.0.1:5000'
FROM_BROKER_ADDRESS = 'tcp://127.0.0.1:5003'

# The default encoding to use for messages
ENCODING = 'utf-8'

# Use these to specify directionality in the EmacsProxy class
(TO, FROM) = ('to', 'from')


# Default Emacs socket server address
EMACS_SERVER_ADDRESS = ('localhost', 14500)

def formatPretty(messageMap):
    """Format messageMap so that it can be print()ed nicely."""
    return json.dumps(messageMap, sort_keys=True, indent=4)

class EmacsProxy:
    def __init__(self, direction):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = direction + "EmacsSocket"
    def connect(self, serverAddress=EMACS_SERVER_ADDRESS):
        """Connect to an Emacs socket server at the specified serverAddress."""
        try:
            self.socket.connect(serverAddress)
            (host, port) = self.socket.getsockname()
            print("Connected {:>15} @ {}:{}".format(self.name, host, port))
            return self
        except ConnectionRefusedError as cre:
            (host, port) = serverAddress
            print("Couldn't connect to {}:{}: {}".format(
                host, port,
                "Connection refused, is the monto.el socket server running?"))
            sys.exit(-1)
    def shakeHands(self, encoding=ENCODING):
        handshake = {'handshake': self.name}
        serializedHandshake = self.serialize(handshake)
        self.socket.send(serializedHandshake.encode(encoding))
        print("Shook hands with Emacs:", formatPretty(handshake))
        return self
    def serialize(self, obj):
        """Serialize an object so that Emacs can process it."""
        return json.dumps(json.dumps(obj))
    def deserialize(self, messageString):
        """Deserialize an Emacs message string to a python object."""
        messageObj = messageString
        while type(messageObj) == str:
            messageObj = json.loads(messageObj)
        if type(messageObj) in [list, dict]:
            return messageObj
        else:
            print("Unsupported deserialized message type:", type(messageObj))
            # TODO: throw a suitable error instead of returning None
            return None
    def send(self, messageMap, encoding=ENCODING):
        """Send messageMap to Emacs."""
        serializedJson = self.serialize(messageMap)
        self.socket.send(serializedJson.encode(encoding))
        print("Sent message to Emacs:", formatPretty(messageMap))
        return self
    def receive(self, maxMsgSize=1024*1024, encoding=ENCODING):
        """Receive a messageMap from Emacs."""
        escapedMsg = self.socket.recv(maxMsgSize).decode(encoding)
        messageMap = self.deserialize(escapedMsg)
        print("Received message:", formatPretty(messageMap))
        return messageMap


class BrokerProxy:
    def __init__(self):
        self.context = zmq.Context()
        self.sockets = {}
        self.toBrokerSocket =   self.context.socket(zmq.REQ)
        self.fromBrokerSocket = self.context.socket(zmq.SUB)
        # TODO: This subscribes to ALL topics:
        self.fromBrokerSocket.setsockopt_string(zmq.SUBSCRIBE, "")
    def connect(self):
        self.toBrokerSocket.connect(TO_BROKER_ADDRESS)
        print("Connected   toBrokerSocket @ {}".format(TO_BROKER_ADDRESS))
        self.fromBrokerSocket.connect(FROM_BROKER_ADDRESS)
        print("Connected fromBrokerSocket @ {}".format(FROM_BROKER_ADDRESS))
        return self
    def __handleAck(self):
        maybeAck = self.toBrokerSocket.recv()
        if maybeAck == b'ack':
            print("Received ACK")
        else:
            print("Instead of ACK, received " + maybeAck)
        pass
    def send(self, messageMap):
        messageString = json.dumps(messageMap, ensure_ascii=False)
        self.toBrokerSocket.send_string(messageString)
        self.__handleAck()
        return self
    def receive(self):
        msg = self.fromBrokerSocket.recv()
        msgObj = json.loads(msg.decode('utf-8'))
        print("msgObj:", formatPretty(msgObj))
        # TODO: ACK to the broker
        return msgObj

#  LocalWords:  usr utf tcp ZmqSocket serverAddress EmacsSocket
#  LocalWords:  EmacsProxy messageMap messageString toBrokerSocket
#  LocalWords:  fromBrokerSocket
