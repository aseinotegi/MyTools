import argparse
from termcolor import colored
import subprocess
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

def def_handler(sig,frame):
    print(colored(f'\n [!] Saliendo del programa... \n', 'red'))
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

def get_arguments():
    parser = argparse.ArgumentParser(description='Herramienta para descubrir los hosts activos en una red ICMP')
    parser.add_argument('-t,','--target', required=True, dest='target', help='Host o rango de red a escanear')

    args= parser.parse_args()

    return args.target

def parse_target(target_str):
    target_str_splitted = target_str.split('.') # ['192', '168','1',1-100']
    firs_three_octets = '.'.join(target_str_splitted[:3])

    if len(target_str_splitted) == 4:
        if '-' in target_str_splitted[3]:
            start, end = target_str_splitted[3].split('-')
            return [f'{firs_three_octets}.{i}'for i in range (int(start), int(end)+1)]
        else:
            return [target_str]
    else:
        print(colored(f'\n [!] Formato de IP o rango incorrecto', 'red'))

def host_discovery(target):
        
    try:
        ping = subprocess.run(["ping", "-n", "1", target], timeout=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if ping.returncode == 0:
            print(colored(f'\t [i] La IP {target} está activa', 'green'))
            
    except subprocess.TimeoutExpired:
        pass


def main():
    target_str = get_arguments()
    targets = parse_target(target_str)
    print(colored(f'\n [+] Host activos en la red : \n ', 'cyan'))
    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(host_discovery, targets)


if __name__ == '__main__':
    main()