
#!/usr/bin/env python3
"""Ataque 4: modificacion controlada de archivo monitoreado por Wazuh FIM."""

import argparse
import datetime
import ipaddress
import pathlib
import subprocess
import sys


ARCHIVO_REMOTO = "/opt/mini-soc/fim/documento-prueba.txt"
USUARIO_PERMITIDO = "fimlab"


def validar_ip(valor):
    try:
        ip = ipaddress.ip_address(valor)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Introduce una direccion IPv4 valida") from exc

    if ip.version != 4 or ip.is_loopback or not (
        ip.is_private or ip in ipaddress.ip_network("100.64.0.0/10")
    ):
        raise argparse.ArgumentTypeError(
            "Solo se permiten direcciones IPv4 privadas del laboratorio"
        )

    return str(ip)


def main():
    parser = argparse.ArgumentParser(
        description="Modificacion autorizada para demostrar Wazuh FIM"
    )

    parser.add_argument("--target", type=validar_ip, required=True)
    parser.add_argument("--ssh-user", default="fimlab")
    parser.add_argument("--ssh-key", required=True)
    parser.add_argument("--lab-confirm", action="store_true", required=True)

    args = parser.parse_args()

    if args.ssh_user != USUARIO_PERMITIDO:
        parser.error("Solo se permite el usuario fimlab")

    clave = pathlib.Path(args.ssh_key).expanduser()

    if not clave.is_file():
        parser.error(f"No existe la clave SSH: {clave}")

    marca = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contenido = f"modificacion-controlada-mini-soc {marca}"

    comando_remoto = (
        "test -f /opt/mini-soc/fim/documento-prueba.txt && "
        "printf '%s\\n' "
        + "'" + contenido + "'"
        + " >> /opt/mini-soc/fim/documento-prueba.txt"
    )

    comando_ssh = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=8",
        "-i", str(clave),
        f"{args.ssh_user}@{args.target}",
        comando_remoto,
    ]

    try:
        resultado = subprocess.run(
            comando_ssh,
            capture_output=True,
            text=True,
            timeout=25,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: tiempo de espera agotado")
        return 1

    carpeta = pathlib.Path.home() / "evidencias"
    carpeta.mkdir(exist_ok=True)

    archivo_evidencia = carpeta / (
        f"04_fim_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
    )

    archivo_evidencia.write_text(
        f"Objetivo: {args.target}\n"
        f"Usuario SSH: {args.ssh_user}\n"
        f"Archivo remoto: {ARCHIVO_REMOTO}\n"
        f"Modificacion enviada: {contenido}\n"
        f"Exit: {resultado.returncode}\n"
        f"Salida: {resultado.stdout}\n"
        f"Error: {resultado.stderr}\n",
        encoding="utf-8",
    )

    if resultado.returncode == 0:
        print("Modificacion remota: OK")
    else:
        print("Modificacion remota: FALLO")
        print(resultado.stderr)

    print(f"Evidencia: {archivo_evidencia}")

    return resultado.returncode


if __name__ == "__main__":
    sys.exit(main())
