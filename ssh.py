from dotenv import load_dotenv
from datetime import datetime
import os
import pandas as pd
from color_alertas import Alerta
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

class SSH:
    def __init__(self, ip, usuario, contrasena):
        self.ip = ip
        self.usuario = usuario
        self.contrasena = contrasena
        self.resultado = {}
        
        # Lista de credenciales alternativas en orden de prioridad
        load_dotenv()
        
        l = os.getenv("L")
        lpass = os.getenv("LPASS")
        
        u = os.getenv("U")
        upass = os.getenv("UPASS")
        
        self.credenciales = [
            (usuario, contrasena),
            (l, lpass),
            (u, upass)
        ]
        
        # Nombre del archivo Excel
        self.excel_file = "network_inventory.xlsx"
    
    def registrar_error(self, mensaje):
        fecha = datetime.now()
        with open("ERRORES.txt", "a") as f:
            f.write(f"{self.ip} : {mensaje} : {fecha}\n")
        Alerta.mensaje("error", f"{mensaje} ")

    def intentar_conectar(self, username, password):
        device = {
            "device_type": "cisco_ios",
            "host": self.ip,
            "username": username,
            "password": password
        }
        comandos = ["show inventory | in SN", "sh ip int brief", "show running-config | include ^interface Vlan|ip address", "show running-config | include hostname"]
        resultado = {}

        try:
            with ConnectHandler(**device) as ssh:
                ssh.enable()
                for comando in comandos:
                    output = ssh.send_command(comando)
                    resultado[comando] = output
                    Alerta.mensaje("correcto", f"Comando '{comando}' ejecutado en {device['host']} ")
            return resultado
        
        except NetmikoTimeoutException:
            self.registrar_error(f"[ERROR] Timeout en {self.ip} (credenciales: {username})")
        except NetmikoAuthenticationException:
            self.registrar_error(f"[ERROR] Autenticación fallida en {self.ip} (credenciales: {username})")
        except Exception as e:
            self.registrar_error(f"[ERROR] Error general en {self.ip}: {e}")
        
        return {}

    def conexion(self):
        for username, password in self.credenciales:
            Alerta.mensaje("info", f"Intentando conexión a {self.ip} con {username} ")
            self.resultado = self.intentar_conectar(username, password)
            if self.resultado:
                break
        return self.resultado

    def parse_inventory(self, inventory_output):
        """Parsea la salida del comando show inventory"""
        serials = []
        for line in inventory_output.split('\n'):
            if 'SN:' in line:
                sn = line.split('SN:')[-1].strip()
                serials.append(sn)
        return serials

    
    def parse_interfaces(self, interface_output):
        interfaces = []
        for line in interface_output.split('\n'):
            # Ignorar líneas vacías y encabezados
            if line and not line.startswith('Interface'):
                parts = line.split()
                # Asegurarse de que haya suficientes columnas en la línea
                if len(parts) >= 6:
                    interface = parts[0]  # Nombre de la interfaz
                    ip = parts[1] if parts[1] != 'unassigned' else ''  # Dirección IP
                    admin_status = parts[4]  # Estado administrativo (columna 5)
                    oper_status = parts[5]  # Estado operativo (columna 6)

                    # Determinar el estado de la interfaz (activa o caída)
                    status = "activa" if admin_status == "up" and oper_status == "up" else "caída"

                    # Agregar la información procesada a la lista
                    interfaces.append({
                        "interface": interface,
                        "ip": ip,
                        "status": status
                    })
        return interfaces


    def parse_vlans(self, vlan_output):
        """Parsea la salida del comando show running-config para VLANs"""
        vlans = []
        current_vlan = None
        
        for line in vlan_output.split('\n'):
            if 'interface Vlan' in line:
                current_vlan = line.split('interface Vlan')[-1].strip()
            elif 'ip address' in line and current_vlan:
                ip = line.split('ip address')[-1].strip()
                vlans.append({"vlan": f"Vlan{current_vlan}", "ip": ip})
                current_vlan = None
        
        return vlans
    
    def parse_hostname(self, hostname_output):
        hostname = []
        for line in hostname_output.split('\n'):
            if 'hostname' in line:
                sn = line.split('hostname')[-1].strip()
                hostname.append(sn)
        return hostname
            
    def save_to_excel(self):
        if not self.resultado:
            mensajeE = Alerta.mensaje("error", f"No hay resultados para {self.ip}")
            self.registrar_error(f"{mensajeE}")
            return
        
        # Obtener los datos parseados
        timestamp = datetime.now()
        serials = self.parse_inventory(self.resultado.get('show inventory | in SN', ''))
        interfaces = self.parse_interfaces(self.resultado.get('sh ip int brief', ''))
        vlans = self.parse_vlans(self.resultado.get('show running-config | include ^interface Vlan|ip address', ''))
        hostname = self.parse_hostname(self.resultado.get('show running-config | include hostname', ''))
        
        # Crear lista de filas para el DataFrame
        rows = []
        
        # Si no hay interfaces ni VLANs, crear al menos una fila con los seriales
        if not interfaces and not vlans:
            rows.append({
                'IP': self.ip,
                'Fecha_Registro': timestamp,
                'Seriales': '; '.join(serials) if serials else 'No SN found',
                'Interfaces': 'No interfaces found',
                'Estado_Interfaz': 'N/A',
                'VLANs': 'No VLANs found',
                'Hostname': '; '.join(hostname) if hostname else 'No hostname found'
            })
        else:
            # Crear una fila por cada interfaz
            for interface in interfaces:
                rows.append({
                    'IP': self.ip,
                    'Fecha_Registro': timestamp,
                    'Seriales': '; '.join(serials) if serials else 'No SN found',
                    'Interfaces': f"{interface['interface']}:{interface['ip']}",
                    'Estado_Interfaz': interface['status'],  # Agregar el estado de la interfaz
                    'VLANs': '',
                    'Hostname': '; '.join(hostname) if hostname else 'No hostname found'
                })
            
            # Crear una fila por cada VLAN
            for vlan in vlans:
                rows.append({
                    'IP': self.ip,
                    'Fecha_Registro': timestamp,
                    'Seriales': '; '.join(serials) if serials else 'No SN found',
                    'Interfaces': '',
                    'Estado_Interfaz': 'N/A',  # No aplica para VLANs
                    'VLANs': f"{vlan['vlan']}:{vlan['ip']}",
                    'Hostname': '; '.join(hostname) if hostname else 'No hostname found'
                })
            
        try:
            # Crear DataFrame con las nuevas filas
            df_new = pd.DataFrame(rows)
            
            # Combinar con datos existentes si el archivo existe
            if os.path.exists(self.excel_file):
                df_existing = pd.read_excel(self.excel_file)
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_combined = df_new
            
            # Guardar el DataFrame en Excel
            df_combined.to_excel(self.excel_file, index=False)
            Alerta.mensaje("correcto", f"Resultados guardados en {self.excel_file}")
            
        except Exception as e:
            self.registrar_error(f"Error al guardar en Excel: {e}")
