import snap7
import ctypes
import time
import random
from snap7.type import SrvArea
import snap7.util

##########################################################################################################################################
##########################################################################################################################################
                                            #PARAMETRIZACION#
##########################################################################################################################################
##########################################################################################################################################

num_dbs = 50  # Número de DBs
db_size = 1440  # Tamaño en bytes de cada DB
port = 1102

##########################################################################################################################################
##########################################################################################################################################
##########################################################################################################################################
##########################################################################################################################################

def initialize_dbs(num_dbs, db_size):
    dbs = {}
    db_structures = []
    formats = ['BOOL', 'INT', 'DINT', 'REAL', 'STRING']

    for i in range(num_dbs):
        db_number = 1000 + i
        data_format = formats[i % len(formats)]  # Cicla entre BOOL, INT, DINT, REAL, STRING
        
        # Ajustar el tamaño máximo de STRING a 254 bytes
        actual_size = db_size if data_format != 'STRING' else min(db_size, 254)
        dbs[db_number] = (ctypes.c_ubyte * actual_size)()
        
        # Inicializar valores según el formato
        if data_format == 'BOOL':
            for bit in range(actual_size * 8):  # BOOLs ocupan bits
                snap7.util.set_bool(dbs[db_number], bit // 8, bit % 8, random.choice([True, False]))
        elif data_format == 'INT':
            for j in range(0, actual_size, 2):  # INT ocupa 2 bytes
                snap7.util.set_int(dbs[db_number], j, random.randint(-32768, 32767))
        elif data_format == 'DINT':
            for j in range(0, actual_size, 4):  # DINT ocupa 4 bytes
                snap7.util.set_dint(dbs[db_number], j, random.randint(-2147483648, 2147483647))
        elif data_format == 'REAL':
            for j in range(0, actual_size, 4):  # REAL ocupa 4 bytes
                snap7.util.set_real(dbs[db_number], j, random.uniform(-1000.0, 1000.0))
        elif data_format == 'STRING':
            max_string_length = min(db_size, 254) - 2
            repeated_string = "Hola Alhona " * (max_string_length // len("Hola Alhona "))
            snap7.util.set_string(dbs[db_number], 0, repeated_string, max_string_length)

        # Guardar la estructura de la DB
        db_structures.append({
            "DB": db_number,
            "Formato": data_format,
            "Tamaño": actual_size
        })
    
    return dbs, db_structures

def export_db_structure_to_file(db_structures, filename="db_structure.txt"):

    with open(filename, "w") as file:
        file.write("Estructura de las DBs del Servidor Snap7\n")
        file.write("=" * 40 + "\n")
        for db in db_structures:
            file.write(f"DB{db['DB']}:\n")
            file.write(f"  Formato: {db['Formato']}\n")
            file.write(f"  Tamaño: {db['Tamaño']} bytes\n")
            file.write("=" * 40 + "\n")
    print(f"Estructura exportada a {filename}")

def main():
    try:
        # Crear servidor
        server = snap7.server.Server()
        print("Servidor Snap7 creado.")

        # Inicializar DBs
        dbs, db_structures = initialize_dbs(num_dbs, db_size)

        # Exportar la estructura de las DBs a un archivo
        export_db_structure_to_file(db_structures)

        # Registrar DBs en el servidor
        for db_number, db_data in dbs.items():
            server.register_area(SrvArea.DB, db_number, db_data)
            print(f"DB{db_number} registrada en el servidor.")

        # Iniciar el servidor
        server.start(tcp_port=port)
        print(f"Servidor Snap7 iniciado en el puerto {port}.")

        # Simulación de cambios en las DBs
        print("Servidor en ejecución. Presiona Ctrl+C para detener.")
        while True:
            for db_number, db_data in dbs.items():
                format_cycle = db_structures[db_number - 1000]['Formato']
                if format_cycle == 'BOOL':
                    for bit in range(db_size * 8):
                        snap7.util.set_bool(db_data, bit // 8, bit % 8, random.choice([True, False]))
                elif format_cycle == 'INT':
                    for j in range(0, db_size, 2):
                        snap7.util.set_int(db_data, j, random.randint(-32768, 32767))
                elif format_cycle == 'DINT':
                    for j in range(0, db_size, 4):
                        snap7.util.set_dint(db_data, j, random.randint(-2147483648, 2147483647))
                elif format_cycle == 'REAL':
                    for j in range(0, db_size, 4):
                        snap7.util.set_real(db_data, j, random.uniform(-1000.0, 1000.0))
                elif format_cycle == 'STRING':
                    max_string_length = min(db_size, 254) - 2
                    repeated_string = "Hola Alhona " * (max_string_length // len("Hola Alhona "))
                    snap7.util.set_string(db_data, 0, repeated_string, max_string_length)
            
            time.sleep(1)  # Actualizar cada segundo

    except KeyboardInterrupt:
        print("\nDeteniendo el servidor...")
        server.stop()
        print("Servidor detenido.")

if __name__ == "__main__":
    main()
