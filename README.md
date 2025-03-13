# Network Device Scanner and Inventory Tool

## Descripción

Esta herramienta automatizada permite escanear, conectar y recopilar información de dispositivos de red Cisco. Diseñada para simplificar la gestión de inventarios de red, la aplicación ofrece las siguientes funcionalidades:

- Escaneo de rangos de IPs para identificar dispositivos accesibles vía SSH o Telnet.
- Conexión automática a los dispositivos usando credenciales proporcionadas.
- Recopilación de información crítica como números de serie, interfaces, VLANs y hostnames.
- Generación de un inventario en formato Excel para facilitar la gestión.

## Características Principales

- Conexión automática a dispositivos Cisco vía SSH (puerto 22) o Telnet (puerto 23).
- Ejecución de comandos predefinidos para recopilar información del inventario.
- Registro detallado de accesos exitosos y fallidos.
- Manejo de credenciales múltiples con soporte para variables de entorno.
- Exportación de datos a Excel con timestamps para el seguimiento del inventario.
- Uso de **multithreading** para mejorar el rendimiento al escanear múltiples dispositivos simultáneamente.

## Requisitos

- Python 3.6+
- Dependencias del proyecto (instalables mediante `requirements.txt`).

## Instalación

1. Clona el repositorio o descarga los archivos.
2. Instala las dependencias necesarias:

   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Crea un archivo `lista_cisco.txt` con las IPs de los dispositivos a escanear, por ejemplo:

   ```txt
   192.168.1.1
   192.168.1.2
   10.0.0.1
   ```

2. (Opcional) Crea un archivo `.env` con credenciales alternativas:

   ```txt
   L=usuario_alternativo
   LPASS=contraseña_alternativa
   U=otro_usuario
   UPASS=otra_contraseña
   ```

3. Ejecuta el programa:

   ```bash
   python main.py
   ```

4. Ingresa las credenciales principales cuando se soliciten.
5. Revisa el archivo `network_inventory.xlsx` para ver los resultados.

## Licencia

Este proyecto está bajo la licencia MIT. Para más información, revisa el archivo `LICENSE`.

---

> *Desarrollado para optimizar la gestión de inventarios de red de dispositivos Cisco.*


