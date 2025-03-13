import os
import getpass
import threading
import time
from scanhosts import ScanHost
from lectura_lista import Lectura
from ssh import SSH
from color_alertas import Alerta
from telnet import CTelnet
from datetime import datetime

def escanear_ip(ip, ports, ips_accesibles, lock):
    """Escanea una IP en busca de puertos abiertos"""
    for port in ports:
        scan = ScanHost(ip, port)
        scan.singleScan()
        if scan.cont() is True:
            with lock:
                ips_accesibles[ip] = port
                with open("IP_CON_ACCESO.txt", "a") as access_ip:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    access_ip.write(f"{timestamp} | {ip} : {port}\n")
            break
    else:
        with lock:
            with open("IP_SIN_ACCESO.txt", "a") as no_access_ip:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                no_access_ip.write(f"{timestamp} | {ip} : Sin acceso en puertos {ports}\n")

def conectar_dispositivo(ip, port, username, password, lock):
    """Conecta a un dispositivo y guarda los resultados en Excel"""
    try:
        if port == 22:
            Alerta.mensaje("info", f"Iniciando conexión SSH para {ip}")
            connection = SSH(ip, username, password)
            result = connection.conexion()
            if result:
                with lock:
                    connection.save_to_excel()
                Alerta.mensaje("correcto", f"Datos de {ip} guardados exitosamente en Excel")
            
        elif port == 23:
            Alerta.mensaje("info", f"Iniciando conexión TELNET para {ip}")
            connection = CTelnet(ip, username, password)
            result = connection.conexion()
            if result:
                with lock:
                    connection.save_to_excel()
                Alerta.mensaje("correcto", f"Datos de {ip} guardados exitosamente en Excel")
                
    except Exception as e:
        Alerta.mensaje("error", f"Error al procesar {ip}: {str(e)}")

def main():
    # Limpiar o crear archivos de registro
    open("IP_CON_ACCESO.txt", "w").close()
    open("IP_SIN_ACCESO.txt", "w").close()
    
    # Solicitar credenciales
    username = input("Ingrese usuario: ")
    password = getpass.getpass("Contraseña: ")

    # Configuración inicial
    file_path = os.path.abspath("lista_cisco.txt")
    ports = [22, 23]
    ips_accesibles = {}
    lock = threading.Lock()

    if not os.path.exists(file_path):
        Alerta.mensaje("error", "No se encontró el archivo lista_cisco.txt")
        return

    # Leer lista de IPs
    try:
        lista = Lectura(file_path)
        lista.lectura()
        ips = lista.obtener_ip_lista()
    except Exception as e:
        Alerta.mensaje("error", f"Error al leer el archivo de IPs: {str(e)}")
        return

    # Fase 1: Escaneo de IPs
    Alerta.mensaje("info", "Iniciando escaneo de IPs...")
    scan_threads = []
    
    for ip in ips:
        thread = threading.Thread(
            target=escanear_ip,
            args=(ip, ports, ips_accesibles, lock)
        )
        scan_threads.append(thread)
        thread.start()
        time.sleep(1)  # Intervalo entre escaneos

    for thread in scan_threads:
        thread.join()

    total_ips = len(ips_accesibles)
    Alerta.mensaje("info", f"Escaneo completado. {total_ips} dispositivos accesibles")
    time.sleep(2)

    # Fase 2: Conexión y recolección de datos
    if total_ips > 0:
        Alerta.mensaje("info", "Iniciando recolección de datos...")
        connect_threads = []

        for ip, port in ips_accesibles.items():
            thread = threading.Thread(
                target=conectar_dispositivo,
                args=(ip, port, username, password, lock)
            )
            connect_threads.append(thread)
            thread.start()
            time.sleep(0.5)  # Intervalo entre conexiones

        for thread in connect_threads:
            thread.join()

        Alerta.mensaje("correcto", "Proceso completado. Revise el archivo Excel para los resultados")
    else:
        Alerta.mensaje("error", "No se encontraron dispositivos accesibles")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Alerta.mensaje("info", "\nProceso interrumpido por el usuario")
    except Exception as e:
        Alerta.mensaje("error", f"Error inesperado: {str(e)}")