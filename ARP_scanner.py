import scapy.all as scapy
import argparse
from termcolor import colored
import sys
import signal

def def_handler(sig, frame):
    print(colored(f'\n [!] Saliendo del programa... \n', 'red'))
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

def get_arguments():
    parser = argparse.ArgumentParser(description='ARP Scanner')
    parser.add_argument('-t', '--target', required=True, dest='target', help='Host o rango de red a escanear')
    args = parser.parse_args()
    return args.target

def scan(ip):
    arp_packet = scapy.ARP(pdst=ip)
    broadcast_packet = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')
    arp_packet = broadcast_packet/arp_packet
    answered, unanswered = scapy.srp(arp_packet, timeout=1, verbose=False)

    response = answered.summary()

    if response:
        print(response)


def main():
    target = get_arguments()
    scan(target)

if __name__ == '__main__':
    main()

