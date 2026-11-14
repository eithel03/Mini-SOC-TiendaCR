#!/usr/bin/env python3
"""Reconocimiento limitado a un solo servidor del laboratorio autorizado."""
import argparse
import datetime
import ipaddress
import pathlib
import subprocess
import sys


def valid_lab_ip(raw):
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Indique una IP IPv4, no un dominio') from exc
    allowed = ip.version == 4 and (ip.is_private or ip in ipaddress.ip_network('100.64.0.0/10'))
    if not allowed or ip.is_loopback or ip.is_multicast or ip.is_unspecified:
        raise argparse.ArgumentTypeError('Solo IP IPv4 privada de laboratorio o Tailscale 100.64.0.0/10')
    return str(ip)


p = argparse.ArgumentParser(description='Ataque 1: escaneo limitado de puertos y servicios con Nmap')
p.add_argument('--target', type=valid_lab_ip, required=True)
p.add_argument('--ports', default='22,80,443,3000,1514,1515', help='Lista de hasta 10 puertos TCP (por defecto 22,80,443,3000,1514,1515)')
p.add_argument('--lab-confirm', action='store_true', required=True, help='Confirma autorizacion del laboratorio')
a = p.parse_args()
try:
    ports = [int(x) for x in a.ports.split(',')]
    if not (1 <= len(ports) <= 10 and all(1 <= x <= 65535 for x in ports)):
        raise ValueError
except ValueError:
    p.error('Use entre 1 y 10 puertos TCP validos separados por comas')
pathlib.Path('evidencias').mkdir(exist_ok=True)
stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
log = pathlib.Path('evidencias') / f'01_nmap_{stamp}.txt'
cmd = ['nmap', '-sT', '-sV', '--version-light', '-Pn', '-T2', '--max-retries', '1', '--host-timeout', '90s', '-p', ','.join(map(str, ports)), a.target]
print('Ejecutando:', ' '.join(cmd), flush=True)
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=110)
except FileNotFoundError:
    sys.exit('Falta Nmap: sudo apt install -y nmap')
except subprocess.TimeoutExpired:
    sys.exit('Nmap excedio el tiempo maximo')
log.write_text(f'Comando: {" ".join(cmd)}\n\n{result.stdout}\n{result.stderr}', encoding='utf-8')
print(result.stdout)
print('Evidencia:', log)
sys.exit(result.returncode)
