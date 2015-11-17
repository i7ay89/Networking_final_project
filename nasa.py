# Itay Parnafes 302698899

import sys
import time
import socket
import struct


default_udp_port                       = 10000
loopback_address                       = '127.0.0.1'
default_filename                       = 'input.txt'
block_size                             = 500 - 20 - 8 - 2
received_buffer_size                   = 20 + 8 + 4
handshake_message                      = 'yo'
default_wait_time                      = 2
handshake_word                         = 'hello'


class Packet(object):
    def __init__(self, seq_number, data, number_of_fragments):
        self.__sequence_number = seq_number
        self.__raw_data = data
        self.__number_of_fragments = number_of_fragments
        self.__data = None
        self._generate_payload()

    def _generate_payload(self):
        packet_header = struct.pack('BB', self.__number_of_fragments, self.__sequence_number)
        self.__data = packet_header + self.__raw_data

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


def send_queued_packets(packets_dictionary, relay_socket, ip_port):
    for packet in packets_dictionary:
        packet.send_packet(relay_socket, ip_port)


def main():
    relay_ip_address = sys.argv[0]
    sock = init_socket()

    fragmented_data = read_file_and_fragment_data()

    connection_established = handshake(sock, (relay_ip_address, default_udp_port))
    if not connection_established:
        print '[!] Was unable to establish connection with relay server...'
        sys.exit()

    i = 0
    packets = {}
    fragment_size = len(fragmented_data)
    for fragment in fragmented_data:
        packet = Packet(i, fragment, fragment_size)
        packets[i] = packet

    done = False
    retransmit = True
    while not done:
        if retransmit:
            send_queued_packets(packets, relay_socket=sock, ip_port=(relay_ip_address, default_udp_port))
            retransmit = False
            timestamp = time.time()
        last_received_packet_raw = sock.recvfrom(received_buffer_size)[0]
        last_received_ack = struct.unpack('B', last_received_packet_raw)

        del packets[last_received_ack]
        if time.time() - timestamp > default_wait_time:
            retransmit = False
        if not packets:
            done = True
