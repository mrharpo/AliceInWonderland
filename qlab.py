# import asyncio
from json import decoder, loads
from socket import socket, AF_INET, SOCK_DGRAM
from time import sleep
from OSC import OSCClient, OSCMessage


from threading import Thread


class Listener:
    def __init__(self, address='0.0.0.0', port=53001):
        print('starting listener')
        self.address = address
        self.port = port
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind((address, port))

    def get_message(self):
        data, address = self.sock.recvfrom(8192)
        raw = data.decode('utf8')
        parts = list(filter(bool, raw.split('\x00')))
        json_message = parts[2]
        try:
            message = loads(json_message)
            if message.get('data'):
                print(message['data'])
            return message
        except decoder.JSONDecodeError as e:
            print('Error. server raw response:', repr(raw))
            print('parts', parts)
            print(e)


class Client:
    def __init__(self, address='127.0.0.1', port=53000):
        self.address = address
        self.port = port
        self.client = OSCClient()
        self.client.connect((address, port))

    def send(self, *args):
        self.client.send(OSCMessage(*args))
        sleep(0.003)


class Interface:
    def __init__(self):
        self.server = Listener()
        self.client = Client()

    def send_and_receive(self, *message):
        self.client.send(*message)
        response = self.server.get_message()
        while not response or message[0] not in response['address']:
            print('wrong response:', response)
            response = self.server.get_message()
        return response
