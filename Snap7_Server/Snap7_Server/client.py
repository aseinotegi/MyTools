import snap7
from snap7.util import get_bool, get_int, get_dint, get_real, get_string
from snap7.type import Areas
import time


##########################################################################################################################################
##########################################################################################################################################
                                            #PARAMETRIZACION#
##########################################################################################################################################
##########################################################################################################################################

    # Configuración inicial
ip_address = '127.0.0.1'  # Dirección del servidor
port = 1102             #puerto
num_dbs = 50            # Número de DBs
db_size = 1440           # Tamaño de cada DB en bytes
formats = ['BOOL', 'INT', 'DINT', 'REAL', 'STRING']  # Formatos cíclicos de las DBs

##########################################################################################################################################
##########################################################################################################################################
##########################################################################################################################################
##########################################################################################################################################


def read_db(client, db_number, db_size, data_format):
    try:
        # Ajustar el tamaño de lectura para STRING
        if data_format == 'STRING':
            max_string_size = min(db_size, 254)  # Tamaño máximo de STRING
            data = client.read_area(Areas.DB, db_number, 0, max_string_size)
        else:
            data = client.read_area(Areas.DB, db_number, 0, db_size)

        print(f"\n--- Leyendo DB{db_number} (Formato: {data_format}, Tamaño: {db_size} bytes) ---")

        if data_format == 'BOOL':
            num_bools = db_size * 8  # Cada byte tiene 8 bits
            bools = [get_bool(data, i // 8, i % 8) for i in range(num_bools)]
            print(f"BOOLs (primeros 50): {bools[:50]}")  # Muestra los primeros 50
        elif data_format == 'INT':
            num_ints = db_size // 2  # Cada INT ocupa 2 bytes
            ints = [get_int(data, i * 2) for i in range(num_ints)]
            print(f"INTs (primeros 20): {ints[:20]}")  # Muestra los primeros 20
        elif data_format == 'DINT':
            num_dints = db_size // 4  # Cada DINT ocupa 4 bytes
            dints = [get_dint(data, i * 4) for i in range(num_dints)]
            print(f"DINTs (primeros 20): {dints[:20]}")  # Muestra los primeros 20
        elif data_format == 'REAL':
            num_reals = db_size // 4  # Cada REAL ocupa 4 bytes
            reals = [get_real(data, i * 4) for i in range(num_reals)]
            print(f"REALs (primeros 20): {reals[:20]}")  # Muestra los primeros 20
        elif data_format == 'STRING':
            # Usar get_string correctamente para extraer la cadena
            value = get_string(data, 0)
            print(f"STRING: {value}")

    except RuntimeError as e:
        print(f"Error al leer la DB{db_number}: {e}")
    except Exception as e:
        print(f"Error inesperado al leer la DB{db_number}: {e}")


def main():

    try:
        # Crear cliente
        client = snap7.client.Client()
        
        # Conectar al servidor
        client.connect(ip_address, 0, 1, tcp_port=port)  # Especificar el puerto 1102

        if client.get_connected():
            print(f"Cliente conectado al servidor en {ip_address} en el puerto 1102.")
        else:
            print("Error al conectar al servidor.")
            return

        # Leer continuamente las DBs
        while True:
            for i in range(num_dbs):
                db_number = 1000 + i
                data_format = formats[i % len(formats)]  # Cicla entre BOOL, INT, DINT, REAL, STRING
                read_db(client, db_number, db_size, data_format)
            time.sleep(5)  # Pausa de 5 segundos antes de la siguiente lectura

    except RuntimeError as e:
        print(f"Error en el cliente: {e}")
    except Exception as e:
        print(f"Error inesperado en el cliente: {e}")

    finally:
        # Desconectar cliente
        client.disconnect()
        print("Cliente desconectado.")

if __name__ == "__main__":
    main()
