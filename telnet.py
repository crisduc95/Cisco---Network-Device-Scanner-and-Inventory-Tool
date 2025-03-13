from dotenv import load_dotenv
from datetime import datetime
import os
import pandas as pd
from color_alertas import Alerta
import xtelnet
from ssh import SSH

class CTelnet(SSH):
    def __init__(self, ip, usuario, contrasena):
        self.ip = ip
        self.usuario = usuario
        self.contrasena = contrasena
        self.resultado = {}

        # Cargar credenciales alternativas desde variables de entorno
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
        Alerta.mensaje("error", f"{mensaje}")

    def intentar_conectar(self, username, password):
        t = xtelnet.Telnet_Session()
        comandos = ["terminal length 0","show inventory | in SN", "sh ip int brief", "show running-config | include ^interface Vlan|ip address", "show running-config | include hostname"]
        resultado = {}

        try:
            # Intentar conectar
            t.connect(self.ip, username=username, password=password, port=23, timeout=5)
            for comando in comandos:
                output = t.execute(
                    comando,
                    timeout=5,
                    buffer_read_timeout=5,
                    remove_prompt_from_output=True,
                    max_empty_buffers=3
                )
                resultado[comando] = output
                Alerta.mensaje("correcto", f"Comando '{comando}' ejecutado en {self.ip}")
            t.close()
            t.destroy()
            return resultado

        except Exception as e:
            self.registrar_error(f"[ERROR] Error en {self.ip} con {username}: {e}")
            return {}

    def conexion(self):
        for username, password in self.credenciales:
            Alerta.mensaje("info", f"Intentando conexión a {self.ip} con {username}")
            self.resultado = self.intentar_conectar(username, password)
            if self.resultado:
                break  # Salir si la conexión es exitosa
        return self.resultado
    
    def parse_inventory(self, inventory_output):
        return super().parse_inventory(inventory_output)
    
    def parse_interfaces(self, interface_output):
        return super().parse_interfaces(interface_output)
    
    def parse_hostname(self, hostname_output):
        return super().parse_hostname(hostname_output)
    
    def parse_vlans(self, vlan_output):
        return super().parse_vlans(vlan_output)
    
    def save_to_excel(self):
        return super().save_to_excel()
