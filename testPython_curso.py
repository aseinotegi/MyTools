import datetime

# Función para procesar los datos y extraer las variables
def procesar_datos(datos, timestamp):
    # Separar las líneas del bloque de datos
    lineas = datos.split('\n')

    # Crear una lista para almacenar los datos procesados
    datos_procesados = []

    # Iterar sobre las líneas para extraer los datos
    for linea in lineas:
        # Verificar si la línea contiene datos
        if ';' in linea:
            # Separar los campos de la línea
            campos = linea.split(';')
            
            # Filtrar campos vacíos
            campos = [campo.strip() for campo in campos if campo.strip() != '']

            # Convertir los campos de interés a los tipos de datos adecuados
            datos_filtrados = [int(campos[1]), float(campos[2].replace(',', '.')), 
                               float(campos[3].replace(',', '.')), float(campos[4].replace(',', '.')),
                               float(campos[5].replace(',', '.')), float(campos[6].replace(',', '.')),
                               float(campos[7].replace(',', '.')), float(campos[8].replace(',', '.')),
                               int(campos[9]), int(campos[10])]

            # Añadir el timestamp a la lista de datos
            datos_filtrados.insert(0, timestamp)

            # Agregar los datos procesados a la lista final
            datos_procesados.append(datos_filtrados)

    return datos_procesados

# Leer el archivo y procesar los datos
with open('pdp1.txt', 'r', encoding='utf-8') as archivo:
    datos_actuales = None
    timestamp = None
    for linea in archivo:
        # Si se encuentra un timestamp, guardar y procesar los datos anteriores
        if 'Rozpocznij Mierzenie:' in linea:
            if datos_actuales is not None:
                datos_procesados = procesar_datos(datos_actuales, timestamp)
                print(datos_procesados)  # Aquí puedes hacer lo que desees con los datos procesados
            datos_actuales = None
            timestamp = datetime.datetime.strptime(linea.strip().split(':')[1].strip(), '%Y-%m-%d %H:%M:%S')
        # Si se encuentra un bloque de datos, almacenarlo
        elif ';' in linea:
            if datos_actuales is None:
                datos_actuales = linea
            else:
                datos_actuales += linea
