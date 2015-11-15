# Itay Parnafes 302698899

import sys
import time
import socket
import struct


default_udp_port                       = 10000
loopback_address                       = '127.0.0.1'
default_filename                       = 'input.txt'
block_size                             = 500 - 20 - 8
received_buffer_size                   = 20 + 8 + 4
seq_mask                               = 0xffffffffff
handshake_message                      = 'yo'
default_wait_time                      = 2
handshake_word                         = 'hello'


class Packet(object):
    def __init__(self, seq_number, data):
        self.__sequence_number = seq_number
        self.__raw_data = data
        self.__data = None
        self._generate_payload()

    def _generate_payload(self):
        seq_header = seq_mask ^ self.__sequence_number
        self.__data = struct.pack('ls', seq_header, self.__raw_data)

    def send_packet(self, relay_socket, ip_port=(loopback_address, default_udp_port)):
        relay_socket.send_to(self.__data, ip_port)


def init_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    return sock


def handshake(relay_socket, ip_port=(loopback_address, default_udp_port)):
    relay_socket.setblocking(1)
    reply = ''
    while not reply:
        try:
            relay_socket.send_to(handshake_message, ip_port)
            relay_socket.settimeout(5)
            reply = relay_socket.recvfrom(block_size)[0]

        except socket.timeout:
            pass

    if reply == handshake_word:
        relay_socket.setblocking(0)
        return True
    return False


def send_ack(sequence_number, relay_socket, ip_port):
    seq_ack_to_send = seq_mask ^ sequence_number
    relay_socket.send_to(seq_ack_to_send, ip_port)


def main():
    relay_ip_address = sys.argv[0]
    sock = init_socket()

    connection_established = handshake(sock, ip_port=(relay_ip_address, default_udp_port))
    if not connection_established:
        print '[!] Was unable to establish connection with relay server...'
        sys.exit()

