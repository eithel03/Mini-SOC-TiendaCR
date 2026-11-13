
# Mini SOC - TiendaCR

## Descripción

Proyecto académico de Seguridad de TI II orientado al diseño e implementación de un Centro de Operaciones de Seguridad (Mini SOC) para una aplicación web vulnerable en un entorno controlado.

El laboratorio utilizará Suricata para la detección de intrusiones de red y Wazuh como plataforma centralizada de monitoreo, análisis de eventos y respuesta ante incidentes.

## Arquitectura del laboratorio

El entorno se implementa mediante máquinas virtuales independientes.

| Componente | Sistema operativo | Función |
|---|---|---|
| SOC-Objetivo | Ubuntu Server 24.04 LTS | Aplicación vulnerable, Docker, Suricata y agente Wazuh |
| SOC-Wazuh | Ubuntu Server 24.04 LTS | Wazuh Server, Indexer y Dashboard |
| Máquina atacante | Kali Linux | Ejecución de pruebas de seguridad controladas |

### Infraestructura

- Hipervisor: Oracle VirtualBox.
- Red NAT: acceso a Internet para actualizaciones.
- Red Host-only: comunicación entre servidores.
- Conectividad remota: pendiente de configurar para la máquina atacante.
- Administración: SSH mediante PowerShell.
- Control de versiones: Git y GitHub.

## Herramientas previstas

- Ubuntu Server 24.04 LTS
- Kali Linux
- Docker
- Aplicación web vulnerable (por seleccionar)
- Suricata
- Wazuh
- OpenSSH
- Git y GitHub

## Estructura del repositorio

- `scripts/`: scripts de instalación, automatización y respuesta.
- `configuraciones/`: archivos de configuración de las herramientas.
- `reglas/`: reglas personalizadas de Suricata y Wazuh.
- `diagramas/`: diagramas de arquitectura.
- `evidencias/`: capturas y resultados de las pruebas.

## Objetivos de implementación

1. Desplegar una aplicación web vulnerable en un entorno controlado.
2. Implementar detección de intrusiones mediante Suricata.
3. Centralizar eventos y alertas con Wazuh.
4. Crear reglas de detección personalizadas.
5. Configurar mecanismos de respuesta automática.
6. Ejecutar y documentar ataques controlados.
7. Aplicar medidas de remediación y verificar su efectividad.

## Estado del proyecto

- [x] Instalación del servidor objetivo.
- [x] Instalación del servidor SIEM.
- [x] Configuración básica de red.
- [x] Comunicación entre servidores.
- [x] Acceso SSH.
- [x] Actualización inicial de los sistemas.
- [ ] Instalación de Docker.
- [ ] Despliegue de la aplicación vulnerable.
- [ ] Instalación y configuración de Wazuh.
- [ ] Instalación y configuración de Suricata.
- [ ] Creación de reglas personalizadas.
- [ ] Configuración de respuestas automáticas.
- [ ] Ejecución de pruebas de seguridad.
- [ ] Remediación y validación.
- [ ] Documentación final.

## Seguridad

Todas las pruebas se realizarán exclusivamente sobre los sistemas autorizados del laboratorio.

No se almacenarán contraseñas, claves privadas, tokens ni otros secretos en el repositorio público.

## Autores

Proyecto académico desarrollado por estudiantes de Ingeniería en Tecnologías de la Información de la Universidad Técnica Nacional, Costa Rica.
