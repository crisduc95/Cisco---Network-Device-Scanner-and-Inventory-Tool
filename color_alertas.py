from colorama import Fore, Style

class Alerta:
    def __init__(self, mensaje=""):
        self.mensaje = mensaje
    
    @staticmethod
    def mensaje(type , mensaje):
        color = ""
        if type.lower() == 'error':
            print(f"{type.upper()} {Fore.LIGHTRED_EX} {mensaje}{Style.RESET_ALL}")
        elif type.lower() == 'info':
            print(f"{type.upper()} {Fore.LIGHTYELLOW_EX} {mensaje}{Style.RESET_ALL}")
        elif type.lower() == 'correcto':
            print(f"{type.upper()} {Fore.LIGHTGREEN_EX} {mensaje}{Style.RESET_ALL}")
        else:
             print(f"{type.upper()}: {mensaje}")
            
        