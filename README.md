# Cisco---Network-Device-Scanner-and-Inventory-Tool
Este proyecto es una herramienta automatizada para escanear, conectar y recopilar información de dispositivos de red Cisco.

Network Device Scanner and Inventory Tool
Este proyecto es una herramienta automatizada para escanear, conectar y recopilar información de dispositivos de red Cisco. Diseñada para simplificar la gestión de inventarios de red, esta aplicación permite:

Escanear rangos de IPs para encontrar dispositivos accesibles vía SSH o Telnet
Conectarse automáticamente a los dispositivos usando credenciales proporcionadas
Recopilar información crítica como números de serie, interfaces, VLANs y hostnames
Generar un inventario completo en formato Excel para facilitar la gestión

La herramienta utiliza multithreading para mejorar el rendimiento al escanear múltiples dispositivos simultáneamente y maneja automáticamente distintos métodos de conexión (SSH/Telnet) según la disponibilidad del dispositivo.
Características principales:

Conexión automática a dispositivos Cisco vía SSH (puerto 22) o Telnet (puerto 23)
Ejecución de comandos predefinidos para recopilar información del inventario
Registro detallado de accesos exitosos y fallidos
Manejo de credenciales múltiples con soporte para variables de entorno
Exportación de datos a Excel con timestamps para seguimiento del inventario

Cómo usar

Asegúrate de tener Python 3.6+ instalado
Instala las dependencias:
pip install -r requirements.txt

Crea un archivo lista_cisco.txt con las IPs de los dispositivos a escanear:

192.168.1.1
192.168.1.2
10.0.0.1

Opcionalmente, crea un archivo .env con credenciales alternativas:

L=usuario_alternativo
LPASS=contraseña_alternativa
U=otro_usuario
UPASS=otra_contraseña

python main.py

Ingresa las credenciales principales cuando se soliciten
Revisa el archivo network_inventory.xlsx para ver los resultados
