__author__ = 'user'

import sys
import time
import socket

default_udp_port    = 10000
loopback_address    = '127.0.0.1'
default_filename    = 'input.txt'
block_size          = 500 - 20 - 8
seq_mask = 0xffffffffffff


class Packet(object):
    def __init__(self, seq_number, data):
        self.__sequence_number = seq_number
        self.__raw_data = data
        self.__data = None
        self._generate_payload()

    def _generate_payload(self):
        seq_header = seq_mask ^ self.__sequence_number
        self.__data = str(seq_header) + self.__raw_data

    def send_packet(self, relay_socket, ip_port=(loopback_address, default_udp_port)):
        relay_socket.send_to(self.__data, ip_port)


def read_file_and_fragment_data():
    f = open(default_filename, 'rb')
    fragmented_data = []
    data = f.read(block_size)
    i = 0
    while data:
        fragmented_data[i] = data
        data = f.read(block_size)
        i += 1
    return fragmented_data

def extract_sequence_number(packet_data):
    return packet_data ^ seq_mask

def init_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def main():
    sock = init_socket()
