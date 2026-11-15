# Mini SOC - TiendaCR

## Descripción

Proyecto académico del curso **ITI-922 Seguridad de TI II** de la Universidad Técnica Nacional (Costa Rica). Consiste en el diseño, implementación y prueba de un **Centro de Operaciones de Seguridad (Mini SOC)** para la tienda ficticia **TiendaCR**, utilizando un laboratorio local y aislado en Oracle VirtualBox.

El laboratorio combina **Suricata** (IDS de red), **Wazuh** (SIEM/HIDS, monitoreo de integridad, detección de vulnerabilidades y respuesta automática), **Docker / OWASP Juice Shop** (aplicación deliberadamente vulnerable) y controles de acceso mediante **UFW, OpenSSH, Nginx y OWASP ModSecurity CRS**.

**Alcance:** exclusivamente equipos propios y direcciones privadas autorizadas del laboratorio. No ejecutar las pruebas sobre servicios ajenos ni publicar este entorno vulnerable en Internet.

## Arquitectura del laboratorio

| Componente | Sistema operativo | IP Host-only | Función |
|---|---|---|---|
| SOC-Objetivo | Ubuntu Server 24.04 LTS | `192.168.56.104` | Docker, Juice Shop, Nginx, ModSecurity CRS, Suricata, Wazuh Agent, UFW y FIM |
| SOC-Wazuh | Ubuntu Server 24.04 LTS | `192.168.56.103` | Wazuh Manager, Indexer, Dashboard y detección de vulnerabilidades |
| Máquina atacante | Kali Linux | `192.168.56.105` | Cuatro pruebas de seguridad controladas |
| Equipo administrador | Windows 11 | `192.168.56.1` | Administración SSH por llaves, navegador del SIEM y Git/GitHub |

### Infraestructura y comunicaciones

- Hipervisor: Oracle VirtualBox.
- Interfaz NAT en las máquinas que lo requieren para obtener actualizaciones.
- Red **Host-only** `192.168.56.0/24` para los servicios y pruebas del laboratorio; las IP son ejemplos de la implementación realizada, no valores obligatorios en otra instalación.
- Políticas UFW de **denegación por defecto** para conexiones entrantes, con excepciones limitadas a las IP y puertos necesarios.
- Acceso SSH por **clave pública**, sin autenticación por contraseña ni acceso directo como `root`.
- Acceso a la aplicación de pruebas: `http://192.168.56.104:3000` únicamente dentro de la red autorizada.
- Wazuh Agent y los eventos de Suricata del servidor objetivo se centralizan en SOC-Wazuh. El Dashboard se consulta desde el equipo administrador usando el puerto HTTPS configurado en el SIEM.

### Diagramas

Los tres diagramas se almacenan en [`diagramas/`](diagramas/):

1. **Arquitectura general:** máquinas, IP, funciones y enlaces del Mini SOC.
2. **Flujo de tráfico y protección web:** UFW → Nginx → ModSecurity CRS → Juice Shop.
3. **Flujo de detección y respuesta automática:** Kali → Suricata → Wazuh Agent/Manager → `firewall-drop` → desbloqueo.

> Los diagramas representan el laboratorio. En particular, la limitación HTTP 429 la aplica **Nginx** y el bloqueo HTTP 403 por SQLi lo aplica **ModSecurity**; el bloqueo temporal `firewall-drop` se ejecuta en **SOC-Objetivo**.

## Herramientas implementadas

| Herramienta | Uso |
|---|---|
| Ubuntu Server 24.04 LTS y Kali Linux | Servidores objetivo/SIEM y atacante controlado |
| Docker Compose | Despliegue de la aplicación web y sus proxies de seguridad |
| OWASP Juice Shop | Aplicación web deliberadamente vulnerable |
| Nginx | Reverse proxy y limitación de solicitudes al inicio de sesión |
| OWASP ModSecurity CRS | WAF con reglas de protección web, incluida detección de SQLi |
| Suricata | Inspección del tráfico y reglas personalizadas |
| Wazuh | Agente, gestor central, panel, FIM, detección de vulnerabilidades y Active Response |
| UFW / OpenSSH | Control de red y administración mediante claves SSH |
| Git / GitHub | Control de versiones, evidencias y trabajo colaborativo |

## Estructura del repositorio

```text
Mini-SOC-TiendaCR/
├── README.md
├── diagramas/                  # Arquitectura y flujos (PNG)
├── configuraciones/
│   ├── docker/
│   │   ├── compose.yaml       # Juice Shop + WAF + Nginx
│   │   └── nginx/
│   │       └── nginx.conf     # Proxy inverso y limitación de login
│   ├── ssh/
│   │   └── 00-mini-soc-hardening.conf
│   └── ...                    # Configuraciones adicionales respaldadas
├── reglas/                     # Reglas de Suricata y Wazuh
├── scripts/                    # Scripts de las pruebas controladas
└── evidencias/
    ├── ...                     # Capturas y resultados de los cuatro ataques
    └── remediacion/            # Comparaciones antes/después y validación final
```

La distribución exacta y los nombres de otros archivos dentro de `reglas/`, `scripts/` y `configuraciones/` se consultan en el árbol del repositorio. Se conservan allí las copias de las reglas y los scripts utilizados en el laboratorio; **no** se incluyen archivos secretos ni claves privadas.

## Reproducción del entorno

### 1. Requisitos previos

- Computadora con virtualización habilitada, **Oracle VirtualBox** y memoria suficiente para ejecutar las máquinas. Una referencia práctica es un equipo con 16 GB RAM, ajustando la asignación según los requisitos de Wazuh.
- Dos VM Ubuntu Server 24.04 LTS y una VM Kali Linux.
- Acceso a Internet mediante NAT **solo para descargar e instalar dependencias**.
- Red Host-only común entre las tres VM y el anfitrión Windows.
- Python 3 en Kali y llave SSH propia para los usuarios administrativos y el usuario de pruebas FIM.
- Una copia local de este repositorio:

```bash
git clone https://github.com/eithel03/Mini-SOC-TiendaCR.git
cd Mini-SOC-TiendaCR
```

### 2. Crear la red del laboratorio

1. Configurar en VirtualBox la red Host-only `192.168.56.0/24` y, cuando corresponda, un adaptador NAT.
2. Asignar direcciones Host-only a las VM: SOC-Objetivo `192.168.56.104`, SOC-Wazuh `192.168.56.103` y Kali `192.168.56.105` (o cambiar coherentemente los destinos y las reglas si se eligen otras IP).
3. Confirmar conectividad entre las VM y configurar las rutas/interfaces correctas.
4. Habilitar UFW con política entrante restrictiva y **permitir primero el acceso SSH autorizado** para evitar perder acceso. Autorizar únicamente los puertos imprescindibles para la aplicación, Wazuh y la administración, desde IP de laboratorio permitidas. No copiar reglas permisivas a una red pública.
5. Instalar y habilitar SSH en ambos servidores, generar **en cada cliente** sus propias llaves y registrar únicamente las llaves públicas en `authorized_keys`.

### 3. Endurecer SSH

Aplicar en **SOC-Objetivo y SOC-Wazuh** el archivo de referencia [`configuraciones/ssh/00-mini-soc-hardening.conf`](configuraciones/ssh/00-mini-soc-hardening.conf) a `/etc/ssh/sshd_config.d/00-mini-soc-hardening.conf`. Validar y reiniciar **solo después de comprobar el acceso con una segunda sesión por llave**:

```bash
sudo sshd -t
sudo sshd -T | grep -E '^(pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication|permitrootlogin) '
sudo systemctl restart ssh
```

El estado esperado es `pubkeyauthentication yes`, `passwordauthentication no`, `kbdinteractiveauthentication no` y `permitrootlogin no`. La contraseña que solicita `sudo` localmente **no es** autenticación SSH.

Ejemplo de conexión desde Windows, con una llave **creada localmente y no guardada en Git**:

```powershell
ssh -i "$HOME\.ssh\mini_soc_ed25519" socadmin@192.168.56.104
ssh -i "$HOME\.ssh\mini_soc_ed25519" socadmin@192.168.56.103
```

### 4. Instalar Wazuh y configurar el agente

1. En **SOC-Wazuh**, instalar componentes compatibles de **Wazuh Manager, Indexer y Dashboard** siguiendo la [documentación oficial de Wazuh](https://documentation.wazuh.com/current/installation-guide/index.html). Para el laboratorio realizado se utilizó la versión 4.14.10.
2. Restringir el acceso al Dashboard y los puertos de agente mediante UFW; conservar las credenciales de instalación **fuera** de Git.
3. En **SOC-Objetivo**, instalar un Wazuh Agent compatible y registrarlo en el Manager de `192.168.56.103`.
4. Configurar monitoreo de registros de autenticación y lectura de eventos de Suricata (`/var/log/suricata/eve.json`).
5. Activar FIM en tiempo real para `/opt/mini-soc/fim`, creando el archivo de prueba `/opt/mini-soc/fim/documento-prueba.txt` con permisos apropiados para el usuario restringido `fimlab`.
6. Activar la detección de vulnerabilidades y la integración del Indexer en el Manager.
7. Verificar en el Dashboard que el agente `SOC-Objetivo` esté conectado, que lleguen alertas y que se muestre Vulnerability Detection.

**Nota de reproducción:** los fragmentos y respaldos de configuración del repositorio sirven de referencia, pero los identificadores de agentes, contraseñas, certificados y ajustes generados durante la instalación deben crearse de nuevo para cada entorno.

### 5. Instalar Suricata y sus reglas

1. Instalar Suricata en SOC-Objetivo siguiendo la [documentación oficial](https://docs.suricata.io/); la implementación probada utilizó Suricata 7.0.3.
2. Configurar la inspección de la interfaz de laboratorio (en la implementación: `enp0s8`) y las redes autorizadas de `HOME_NET`.
3. Copiar y habilitar las reglas propias almacenadas en [`reglas/`](reglas/), incluido el archivo de reglas del Mini SOC, en la ruta de reglas que use Suricata (por ejemplo, `/etc/suricata/rules/`). Verificar que `suricata.yaml` las cargue.
4. Validar la configuración con `suricata -T` y reiniciar el servicio. Revisar `/var/log/suricata/fast.log` y `/var/log/suricata/eve.json`.
5. Confirmar que los eventos JSON llegan al agente Wazuh y al Dashboard central.

**Reglas Suricata comprobadas:** SID `1000002` (solicitudes repetidas a `/rest/user/login`) y SID `1000003` (SQLi en la aplicación). El SID `1000001` también forma parte del catálogo de reglas personalizadas de la implementación. La detección de reconocimiento puede involucrar reglas de anomalías del protocolo y no necesariamente un SID que identifique Nmap por su nombre.

### 6. Desplegar Juice Shop con Nginx y WAF

En **SOC-Objetivo**, instalar Docker Engine y Docker Compose Plugin y copiar los archivos de [`configuraciones/docker/`](configuraciones/docker/) a un directorio de despliegue, conservando la relación entre `compose.yaml` y `nginx/nginx.conf`:

```bash
mkdir -p ~/mini-soc/juice-shop/nginx
# Copiar compose.yaml y nginx/nginx.conf desde el repositorio a este directorio.
cd ~/mini-soc/juice-shop
docker compose config
docker compose up -d
docker compose ps
```

Flujo real: **cliente → Nginx → OWASP ModSecurity CRS (WAF) → OWASP Juice Shop**.

- Nginx expone la aplicación a la IP privada autorizada en el puerto `3000` y limita las solicitudes al endpoint `/rest/user/login`, con respuesta **HTTP 429** cuando se supera el umbral.
- ModSecurity CRS inspecciona las solicitudes y puede bloquear SQLi con **HTTP 403** (reglas CRS `942100` y `949110` registradas en la prueba).
- Juice Shop continúa siendo una aplicación de entrenamiento vulnerable; el WAF es una **mitigación externa**, no una corrección de su código fuente.

Revisar los puertos y direcciones publicados en `compose.yaml` antes de levantar el servicio: cualquier IP de acceso adicional, como una IP Tailscale específica del laboratorio original, debe actualizarse o eliminarse si no existe en el entorno replicado.

### 7. Configurar la respuesta automática

En SOC-Wazuh, incorporar las reglas personalizadas del repositorio al motor de Wazuh, con la regla **`100100` (nivel 10)** para solicitudes repetidas detectadas por Suricata. Configurar la respuesta **`firewall-drop`** para el agente SOC-Objetivo con bloqueo temporal de la IP atacante, y comprobar las reglas/eventos **`651` (bloqueo)** y **`652` (desbloqueo)**.

Confirmar que la IP o interfaz de administración no se bloquee accidentalmente. Ajustar el tiempo de respuesta y documentar el riesgo de falsos positivos. En el laboratorio se comprobó un bloqueo aproximado de **60 segundos**.

## Ejecución de los cuatro ataques controlados

Realizar las pruebas **únicamente desde Kali y contra SOC-Objetivo en la red autorizada**. Los scripts del repositorio deben estar presentes en Kali (por ejemplo, copiados a `~/`). El parámetro `--lab-confirm` exige confirmación explícita del contexto de laboratorio.

| N.º | Prueba | Objetivo y evidencia esperada |
|---|---|---|
| 1 | Reconocimiento con Nmap | Escaneo de puertos/servicios y alerta de red Suricata visible en Wazuh |
| 2 | Ocho solicitudes de inicio de sesión con credenciales inválidas | Suricata SID `1000002`, Wazuh regla `100100`, y bloqueo/desbloqueo automático `651/652` |
| 3 | Inyección SQL de laboratorio | Alerta de Suricata y registros de la aplicación; después del WAF, rechazo HTTP 403 |
| 4 | Modificación controlada de archivo | Evento FIM sobre `/opt/mini-soc/fim/documento-prueba.txt` visible en Wazuh |

### Ataque 1: reconocimiento

```bash
python3 ~/01_reconocimiento_nmap.py --help
```

El script permite consultar su sintaxis exacta, que debe respetarse al reproducir la prueba. Requiere contar con Nmap instalado en Kali.

### Ataque 2: autenticación repetida

```bash
python3 ~/02_intentos_login.py --target 192.168.56.104 --lab-confirm
```

El script envía ocho solicitudes a `http://192.168.56.104:3000/rest/user/login` y guarda un registro JSONL en `evidencias/` del directorio de ejecución. La regla propia detecta **peticiones repetidas al endpoint**; no se debe interpretar automáticamente como prueba de ocho contraseñas rechazadas sin cotejar el registro web.

### Ataque 3: SQLi

```bash
python3 ~/03_sql_injection_juice_shop.py --target 192.168.56.104 --lab-confirm
```

Antes de la remediación se registró el comportamiento vulnerable de la aplicación en el laboratorio; después se verificó el **HTTP 403 del WAF**. No realizar este ejercicio fuera de las VM propias.

### Ataque 4: integridad de archivos (FIM)

Primero crear en SOC-Objetivo el usuario de prueba restringido `fimlab`, su acceso **solo por llave pública**, el directorio monitoreado y el archivo de prueba con los permisos mínimos. En Kali crear una llave **distinta de la llave administrativa** y autorizar solo su clave pública para ese usuario.

```bash
python3 ~/04_integridad_fim.py --target 192.168.56.104 --ssh-user fimlab --ssh-key ~/.ssh/mini_soc_fim_ed25519 --lab-confirm
```

Verificar en Wazuh el evento de modificación del archivo FIM. No incluir la llave privada FIM en Git.

## Detección, validación y evidencias

En SOC-Objetivo:

```bash
sudo grep 'MINI-SOC Multiples solicitudes de autenticacion' /var/log/suricata/fast.log | tail -5
sudo tail -n 12 /var/ossec/logs/active-responses.log
```

En Wazuh Dashboard, abrir **Threat Hunting**, seleccionar el agente `SOC-Objetivo` y buscar las reglas correspondientes a cada ataque. Para la prueba de respuesta automática, comprobar en orden:

1. Suricata SID `1000002` detecta solicitudes repetidas a `/rest/user/login`.
2. Wazuh genera la alerta personalizada `100100`.
3. Active Response ejecuta `firewall-drop` con acción `add` (regla Wazuh `651`).
4. Aproximadamente un minuto después ejecuta `delete` (regla Wazuh `652`).

### Remediación: comparación antes/después

| Ataque | Antes de la remediación | Después de la remediación |
|---|---|---|
| 2: solicitudes de login | Intentos llegan sin el límite adicional de Nginx; detección Suricata/Wazuh y respuesta automática | Nginx devuelve HTTP 429 por exceso de solicitudes; Suricata/Wazuh siguen detectando y `firewall-drop` bloquea temporalmente |
| 3: SQLi | El laboratorio registró una explotación sobre Juice Shop y eventos de detección | ModSecurity CRS bloquea el intento con HTTP 403; Juice Shop sigue siendo vulnerable detrás de la protección |

Las **capturas de los ataques originales** están en [`evidencias/`](evidencias/) y las **capturas de remediación y validación final** en [`evidencias/remediacion/`](evidencias/remediacion/). Las evidencias incluyen resultados de Kali, alertas Wazuh, bloqueo/desbloqueo y registros del WAF. Los tiempos de detección, técnicas MITRE ATT&CK, matriz de riesgos y riesgo residual se desarrollan en el **informe técnico**.

## Objetivos de implementación

- [x] Desplegar aplicación web vulnerable en contenedores y laboratorio controlado.
- [x] Implementar IDS de red con Suricata.
- [x] Centralizar eventos y alertas en Wazuh.
- [x] Crear y probar reglas personalizadas de detección.
- [x] Configurar y comprobar respuesta automática.
- [x] Ejecutar los cuatro ataques controlados.
- [x] Aplicar remediaciones y repetir los ataques 2 y 3.
- [x] Endurecer acceso SSH mediante llaves.
- [x] Comprobar monitoreo FIM y detección de vulnerabilidades.

## Estado del proyecto

**Implementación y validación técnica:** completadas en el laboratorio local. Las capturas y respaldos de configuración están organizados para su publicación en el repositorio.

**Entregables académicos:** README y diagramas; informe técnico PDF de 15 a 20 páginas; demostración presencial de 10 minutos más preguntas; y coevaluación individual. La publicación de cambios y el cierre de estos entregables se gestionan mediante Git/GitHub y los canales del curso.

## Seguridad y ética

- No ejecutar ataques contra sistemas ajenos, Internet público ni recursos universitarios.
- Mantener la red privada, el acceso administrativo restringido y la denegación por defecto.
- No almacenar **contraseñas, claves privadas SSH, archivos `.env` con secretos, tokens, certificados privados o credenciales** en el repositorio ni en capturas.
- Verificar el contenido de archivos antes de hacer `git add` y revisar `git diff --cached` antes de confirmar cambios.
- Considerar el riesgo de falsos positivos del bloqueo automático y habilitar el desbloqueo temporal.
- No interpretar las mitigaciones de Nginx/WAF como eliminación completa de las vulnerabilidades de Juice Shop.
- Documentar en el informe cualquier uso de herramientas de IA, según las instrucciones del curso.

## Organización del trabajo y control de versiones
Inicialmente, se contempló implementar el proyecto en Microsoft Azure debido a las limitaciones de memoria RAM del equipo de uno de los integrantes. Sin embargo, las restricciones relacionadas con los tamaños de las máquinas virtuales disponibles impidieron utilizar esta alternativa, por lo que se decidió desarrollar el laboratorio mediante Oracle VirtualBox.

La distribución inicial consistía en ejecutar los dos servidores principales en el equipo de un integrante y la máquina atacante Kali Linux en el equipo del compañero, estableciendo la comunicación mediante Tailscale. No obstante, durante las pruebas de conectividad se presentaron dificultades de rendimiento en el segundo equipo, incluyendo lentitud excesiva y bloqueos del sistema, lo que impidió trabajar de manera estable.

Ante esta situación, acordamos centralizar la implementación y ejecución del laboratorio en una sola computadora con 16 GB de RAM, manteniendo la colaboración y coordinación mediante Discord.

Por esta razón, el repositorio y la realización de los commits se centralizaron en una única cuenta de GitHub. Esto fue una de las limitaciones técnicas que se presentaron durante el desarrollo del proyecto pero en conjunto logramos llevarlo acabo.

## Autores

Proyecto académico desarrollado por **Eithel Herrera Rojas y Luis Chavala González**, estudiantes de Ingeniería en Tecnologías de la Información de la **Universidad Técnica Nacional (UTN), Costa Rica**.

> Este repositorio se comparte con fines estrictamente educativos y de reproducción en un entorno aislado y autorizado.
