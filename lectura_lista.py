'''
Clase que lee una lista extraida de un archivo y la vuelve una lista (list) para poder recorrerla item por item
'''

class Lectura:

    def __init__(self, archivo, ip_lista=None):
        self.archivo = archivo
        self.ip_lista = ip_lista if ip_lista is not None else []
    
    def lectura(self):
        with open(self.archivo, "r") as file:
            for ip in file:
                self.ip_lista.append(ip.strip())
        print (self.ip_lista)
    
    def obtener_ip_lista(self):
        return self.ip_lista

