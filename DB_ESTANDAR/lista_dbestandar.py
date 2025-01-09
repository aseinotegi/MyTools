import csv

# GET DATA LENGHT
B_Bools = 400
B_Bytes = 0 
B_Int16 = 600
B_Int32 = 152
B_Float = 0
StartBools = 0
StartBytes = B_Bools
StartInt16 = B_Bools + B_Bytes
StartInt32 = B_Bools + B_Bytes + B_Int16
StartFloat = B_Bools + B_Bytes + B_Int16 + B_Int32
StopBools = StartBytes
StopBytes = StartInt16
StopInt16 = StartInt32
StopInt32 = StartFloat
Lenght = B_Bools + B_Bytes + B_Int16 + B_Int32 + B_Float
StopFloat = Lenght

def byteStruct (_byteIn):
    x='null'
    if _byteIn < 10 :
        x = f'00{_byteIn}'
    elif _byteIn >= 10 and _byteIn < 100 :
        x = f'0{_byteIn}'
    elif _byteIn > 100:
        x=_byteIn
    return x
# Función para generar el formato de la lista
def generar_formato():
    lista = []
    if B_Bools > 0 :
        for _byte in range(StartBools,B_Bools):
            byte = byteStruct(_byte)
            for _bit in range(8):
                _bit = f'0{_bit}'
                lista.append(f'Bool_011_o_({byte})_{_bit}')
    if B_Bytes > 0 :
        for _byte in range(StartBytes,B_Bytes):
            byte = byteStruct(_byte)
            lista.append(f'Byte_011_o_({byte})')
    if B_Int16 > 0 :
        for _byte in range(StartInt16,StopInt16,2):
            byte = byteStruct(_byte)
            lista.append(f'Int16_011_o_({byte})')
    if B_Int32 > 0 :
        for _byte in range(StartInt32,StopInt32,4):
            byte = byteStruct(_byte)
            lista.append(f'Int32_011_o_({byte})')
    if B_Float > 0 :
        for _byte in range(StartFloat,StartFloat,4):
            byte = byteStruct(_byte)
            lista.append(f'Float_011_o_({byte})')
    return lista

# Función para exportar la lista a un archivo CSV
def exportar_a_csv(lista):
    with open('lista_dbestandar.csv', 'w', newline='') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        for elemento in lista:
            escritor.writerow([elemento])

# Generar la lista con el formato requerido
lista_formato = generar_formato()

# Exportar la lista a un archivo CSV
exportar_a_csv(lista_formato)

print("Archivo CSV generado exitosamente.")
