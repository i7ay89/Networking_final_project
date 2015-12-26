# Itay Parnafes 302698899

import sys
import time
import socket
import struct


default_udp_port                       = 10000
loopback_address                       = '127.0.0.1'
default_filename                       = 'output.txt'
block_size                             = 500 - 20 - 8
handshake_message                      = 'yo'
default_wait_time                      = 2
handshake_word                         = 'hello'
done_sequence_number                   = 255


def init_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock


def handshake(relay_socket, ip_port=(loopback_address, default_udp_port)):
    reply = ''
    while not reply:
        try:
            relay_socket.sendto(handshake_message, ip_port)
            relay_socket.settimeout(5)
            reply = relay_socket.recvfrom(block_size)[0]
        except socket.timeout:
            pass

    if reply == handshake_word:
        return True
    return False

def reassemble_file(fragmented_data):
    output = open(default_filename, 'wb')
    for fragment in fragmented_data:
        output.write(fragmented_data[fragment])
    output.close()

def response_ack(relay_sock, ip_port, sequence_number):
    data_to_send = struct.pack('B', sequence_number)
    relay_sock.sendto(data_to_send, ip_port)

def main():
    relay_ip_address = sys.argv[1]
    sock = init_socket()

    connection_established = handshake(sock, ip_port=(relay_ip_address, default_udp_port))
    if not connection_established:
        print '[!] Was unable to establish connection with relay server...'
        sys.exit()

    fragmented_data = {}
    done = False
    while not done:
        try:
            received_raw_data = sock.recvfrom(block_size)[0]
            number_of_fragments, sequence_number = struct.unpack('BB', received_raw_data[:2])
            actual_data = received_raw_data[2:]
            fragmented_data[sequence_number] = actual_data
            response_ack(sock, (relay_ip_address, default_udp_port), sequence_number)
        except socket.timeout:
            pass

        if number_of_fragments == len(fragmented_data):
            done = True
            response_ack(sock, (relay_ip_address, default_udp_port), done_sequence_number)

    reassemble_file(fragmented_data)

if __name__ == '__main__':
    main()
