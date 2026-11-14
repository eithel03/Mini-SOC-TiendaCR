#!/usr/bin/env python3
"""Intentos fallidos y limitados en la app deliberadamente vulnerable."""
import argparse
import datetime
import ipaddress
import json
import pathlib
import time
import urllib.error
import urllib.request


def valid_lab_ip(raw):
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Use IPv4 numerica') from exc
    if ip.version != 4 or not (ip.is_private or ip in ipaddress.ip_network('100.64.0.0/10')) or ip.is_loopback:
        raise argparse.ArgumentTypeError('Solo IPv4 privada autorizada o Tailscale')
    return str(ip)


p = argparse.ArgumentParser(description='Ataque 2: 8 autenticaciones invalidas en Juice Shop')
p.add_argument('--target', type=valid_lab_ip, required=True)
p.add_argument('--port', type=int, default=3000)
p.add_argument('--lab-confirm', action='store_true', required=True)
a = p.parse_args()
if not 1 <= a.port <= 65535:
    p.error('Puerto invalido')
pathlib.Path('evidencias').mkdir(exist_ok=True)
log = pathlib.Path('evidencias') / f'02_login_{datetime.datetime.now():%Y%m%d_%H%M%S}.jsonl'
url = f'http://{a.target}:{a.port}/rest/user/login'
print('Enviando 8 intentos invalidos al laboratorio:', url)
with log.open('w', encoding='utf-8') as f:
    for i in range(1, 9):
        payload = json.dumps({'email': 'mini-soc-no-existe@example.invalid', 'password': f'clave-invalida-demo-{i}'}).encode()
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        status = None
        error = None
        try:
            with urllib.request.urlopen(req, timeout=6) as response:
                status = response.status
        except urllib.error.HTTPError as ex:
            status = ex.code
        except (urllib.error.URLError, TimeoutError) as ex:
            error = str(ex)
        row = {'momento': datetime.datetime.now().isoformat(), 'intento': i, 'http_status': status, 'error': error}
        f.write(json.dumps(row) + '\n')
        print(f'Intento {i}: HTTP {status if status is not None else error}')
        time.sleep(1)
print('Registro:', log)
print('Importante: la regla IDS actual detecta multiples peticiones a /rest/user/login; verifique los fallos reales en logs de la aplicacion.')
