#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXX            IMPORT LIBRARIES        XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
import snap7
from snap7 import util
import time
import csv
import os
from datetime import datetime
import struct
import pika
import multiprocessing

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXX            INITIALICE VARIABLES         XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DataChange = {}
AllData = {}
valores_bool = {}
valores_bool_mem = {}
valores_byte = {}
valores_byte_mem = {}
valores_int16 = {}
valores_int16_mem = {}
valores_int32 = {}
valores_int32_mem = {}
valores_float = {}
valores_float_mem = {}
client = False
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXX            GET DATA FROM PLC FUNCTIONS         XXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

def get_bool(bytearray_: bytearray, byte_index: int, bool_index: int) -> bool:
    """Get the boolean value from location in bytearray

    Args:
        bytearray_: buffer data.
        byte_index: byte index to read from.
        bool_index: bit index to read from.

    Returns:
        True if the bit is 1, else 0.

    Examples:
        >>> buffer = bytearray([0b00000001])  # Only one byte length
        >>> get_bool(buffer, 0, 0)  # The bit 0 starts at the right.
            True
    """
    index_value = 1 << bool_index
    byte_value = bytearray_[byte_index]
    current_value = byte_value & index_value
    return current_value == index_value
def get_byte(bytearray_: bytearray, byte_index: int) -> bytes:
    """Get byte value from bytearray.

    Notes:
        WORD 8bit 1bytes Decimal number unsigned B#(0) to B#(255) => 0 to 255

    Args:
        bytearray_: buffer to be read from.
        byte_index: byte index to be read.

    Returns:
        value get from the byte index.
    """
    data = bytearray_[byte_index:byte_index + 1]
    data[0] = data[0] & 0xff
    packed = struct.pack('B', *data)
    value = struct.unpack('B', packed)[0]
    return value
def get_int16(bytearray_: bytearray, byte_index: int) -> int:
    """Get int value from bytearray.

    Notes:
        Datatype `int` in the PLC is represented in two bytes

    Args:
        bytearray_: buffer to read from.
        byte_index: byte index to start reading from.

    Returns:
        Value read.

    Examples:
        >>> data = bytearray([0, 255])
        >>> snap7.util.get_int(data, 0)
            255
    """
    data = bytearray_[byte_index:byte_index + 2]
    data[1] = data[1] & 0xff
    data[0] = data[0] & 0xff
    packed = struct.pack('2B', *data)
    value = struct.unpack('>h', packed)[0]
    return value
def get_float(bytearray_: bytearray, byte_index: int) -> float:
    """Get real value.

    Notes:
        Datatype `real` is represented in 4 bytes in the PLC.
        The packed representation uses the `IEEE 754 binary32`.

    Args:
        bytearray_: buffer to read from.
        byte_index: byte index to reading from.

    Returns:
        Real value.

    Examples:
        >>> data = bytearray(b'B\\xf6\\xa4Z')
        >>> snap7.util.get_real(data, 0)
            123.32099914550781
    """
    x = bytearray_[byte_index:byte_index + 4]
    real = struct.unpack('>f', struct.pack('4B', *x))[0]
    return real
def get_int32(bytearray_: bytearray, byte_index: int) -> int:
    """Get dint value from bytearray.

    Notes:
        Datatype `dint` consists in 4 bytes in the PLC.
        Maximum possible value is 2147483647.
        Lower posible value is -2147483648.

    Args:
        bytearray_: buffer to read.
        byte_index: byte index from where to start reading.

    Returns:
        Value read.

    Examples:
        >>> import struct
        >>> data = bytearray(4)
        >>> data[:] = struct.pack(">i", 2147483647)
        >>> snap7.util.get_dint(data, 0)
            2147483647
    """
    data = bytearray_[byte_index:byte_index + 4]
    dint = struct.unpack('>i', struct.pack('4B', *data))[0]
    return dint

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXX            GET ALL DATA FUNCTION         XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
def GetAllDataPLC (DB,B_Bools,B_Bytes,B_int16,B_int32,B_Float):
        global DataChange
        global AllData
        global valores_bool
        global valores_bool_mem 
        global valores_byte 
        global valores_byte_mem 
        global valores_int16 
        global valores_int16_mem 
        global valores_int32 
        global valores_int32_mem 
        global valores_float 
        global valores_float_mem
        global client
        StartBools = 0
        StartBytes = B_Bools
        StartInt16 = B_Bools + B_Bytes
        StartInt32 = B_Bools + B_Bytes + B_int16
        StartFloat = B_Bools + B_Bytes + B_int16 + B_int32
        #StartString = B_Bools + B_Bytes + B_int16 + B_int32 + B_Float
        DataLenght = B_Bools + B_Bytes + B_int16 + B_int32 + B_Float
        #EndString =(B_Bools + B_Bytes + B_int16 + B_int32 + B_Float + B_String -1 )
        if client.get_connected():
            timestamp = datetime.now()
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            if B_Bools > 0 :   
                _bool = 0
                Bytedata = client.db_read(DB, StartBools, B_Bools)
                for _bool in range(B_Bools):
                    for _bit in range(8):
                        valor = get_bool(Bytedata, _bool, _bit)
                        nombre_variable = f'byte{_bool}_bit{_bit}'
                        valores_bool[nombre_variable] = valor
                        valores_bool_mem[nombre_variable]=valores_bool[nombre_variable]
                        AllData.update({nombre_variable: valor})
                        #print(f"{nombre_variable},{valor}")            

            if B_Bytes> 0 :
                    byte = 0
                    Bytedata = client.db_read(DB, StartBytes, B_Bytes)
                    for byte in range(B_Bytes):
                            valor = get_byte(Bytedata, byte)
                            nombre_variable = f'byte{byte}'
                            valores_byte[nombre_variable] = valor
                            valores_byte_mem[nombre_variable]=valores_byte[nombre_variable]
                            AllData.update({nombre_variable: valor})           
                            #print(f"{nombre_variable},{valor}")
            if B_int16> 0 :
                    _int16 = 0
                    Bytedata = client.db_read(DB, StartInt16, B_int16)
                    for _int16 in range(0,B_int16,2):
                            valor = get_int16(Bytedata, _int16)
                            nombre_variable = f'int16,{_int16}'
                            valores_int16[nombre_variable] = valor
                            valores_int16_mem[nombre_variable]=valores_int16[nombre_variable]
                            AllData.update({nombre_variable: valor})  
                            #print(f"{nombre_variable},{valor}")           

            if B_int32> 0 :
                    _int32 = 0
                    Bytedata = client.db_read(DB, StartInt32, B_int32)
                    for _int32 in range(0,B_int32,4):
                            valor = get_int32(Bytedata, _int32)
                            nombre_variable = f'int32,{_int32}'
                            valores_int32[nombre_variable] = valor
                            valores_int32_mem[nombre_variable]=valores_int32[nombre_variable]
                            AllData.update({nombre_variable: valor})
                            #print(f"{nombre_variable},{valor}")

            if B_Float> 0 :
                    _float = 0
                    Bytedata = client.db_read(DB, StartFloat, B_Float)
                    for _float in range(0,B_Float,4):
                            valor = get_float(Bytedata, _float)
                            nombre_variable = f'Float{_float}'
                            valores_float[nombre_variable] = valor
                            valores_float_mem[nombre_variable]=valores_float[nombre_variable]
                            AllData.update({nombre_variable: valor})
        AllData["Timestamp"] = timestamp_str
        print(AllData)
        return AllData

#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXX            GET CHANGE DATA FUNCTION         XXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
def GetDataChange(DB,B_Bools,B_Bytes,B_int16,B_int32,B_Float):
        global DataChange
        global AllData
        global valores_bool
        global valores_bool_mem 
        global valores_byte 
        global valores_byte_mem 
        global valores_int16 
        global valores_int16_mem 
        global valores_int32 
        global valores_int32_mem 
        global valores_float 
        global valores_float_mem
        global client
        StartBools = 0
        StartBytes = B_Bools
        StartInt16 = B_Bools + B_Bytes
        StartInt32 = B_Bools + B_Bytes + B_int16
        StartFloat = B_Bools + B_Bytes + B_int16 + B_int32
        #StartString = B_Bools + B_Bytes + B_int16 + B_int32 + B_Float
        DataLenght = B_Bools + B_Bytes + B_int16 + B_int32 + B_Float
        #EndString =(B_Bools + B_Bytes + B_int16 + B_int32 + B_Float + B_String -1 )

        if client.get_connected():
            timestamp = datetime.now()
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            DataChange = {}
            Bytedata = client.db_read(DB, 0,DataLenght)
            ejecute = False 
            if B_Bools > 0 :
                byte_bits = [list(map(int, bin(byte)[2:].rjust(8, '0'))) for byte in Bytedata]
                for _byte in range(StartBools,B_Bools):
                    for _bit in range(8):
                        valor = byte_bits[_byte][_bit]
                        nombre_variable = f'byte{_byte}_bit{_bit}'
                        valores_bool[nombre_variable] = valor
                        if valores_bool[nombre_variable] != valores_bool_mem[nombre_variable]:
                            DataChange.update({nombre_variable: valor})
                            valores_bool_mem[nombre_variable] = valores_bool[nombre_variable]
                            ejecute = True
        
            if B_Bytes> 0 :
                    for _byte in range(StartBytes,B_Bytes):
                            valor = get_byte(Bytedata, _byte)
                            nombre_variable = f'byte{_byte}'
                            valores_byte[nombre_variable] = valor
                            if valores_byte[nombre_variable] != valores_byte_mem[nombre_variable]:
                                DataChange.update({nombre_variable: valor})       
                                valores_byte_mem[nombre_variable] = valores_byte[nombre_variable]
                                ejecute = True
            if B_int16> 0 :
                    for _byte in range(StartInt16,B_int16,2):
                            valor = get_int16(Bytedata, _byte)
                            nombre_variable = f'int16,{_byte}'
                            valores_int16[nombre_variable] = valor
                            if valores_int16[nombre_variable] != valores_int16_mem[nombre_variable]:
                               DataChange.update({nombre_variable: valor}) 
                               valores_int16_mem[nombre_variable] = valores_int16[nombre_variable]
                               ejecute = True
                             
            if B_int32> 0 :              
                    for _byte in range(StartInt32,B_int32,4):
                            valor = get_int32(Bytedata, _byte)
                            nombre_variable = f'int32,{_byte}'
                            valores_int32[nombre_variable] = valor
                            if valores_int32[nombre_variable] != valores_int32_mem[nombre_variable]:
                               DataChange.update({nombre_variable: valor})
                               valores_int32_mem[nombre_variable] = valores_int32[nombre_variable]
                               ejecute = True   
                                   

            if B_Float> 0 :     
                    for _byte in range(StartFloat,B_Float,4):
                            valor = get_float(Bytedata, _byte)
                            nombre_variable = f'Float{_byte}'
                            valores_float[nombre_variable] = valor
                            if valores_float[nombre_variable] != valores_float_mem[nombre_variable]:
                                DataChange.update({nombre_variable: valor})
                                valores_float_mem[nombre_variable] = valores_float[nombre_variable]
                                ejecute = True
        if ejecute :
         DataChange["Timestamp"] = timestamp_str             
        stop_time = time.monotonic()
        '''
        if ejecute:
                #print(f"T-ReadDataFromPLC {CycleScan}")
                print(DataChange)
        return DataChange
'''
def PublishRabbitMQ(PublishData):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='datos_plc',durable=True)
    channel.basic_publish(exchange='', routing_key='datos_plc', body=str(PublishData))
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXX                                            XXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXX            START EJECUTION PROGRAM         XXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXX                                            XXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
#                                     PARAMETRIZACION
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

IP = "192.168.10.2"
DB = 2501
I_Bools = 400
I_bytes = 0 
I_int16 = 600
I_int32 = 152
I_Float = 0
#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
FirstTime = False
while True:
    if not FirstTime:
        client = snap7.client.Client()
        client.connect(IP, 0, 1)
        GetAllDataPLC(DB,B_Bools=I_Bools,B_Bytes=I_bytes,B_int16=I_int16,B_int32=I_int32,B_Float=I_Float)
        FirstTime=True
    else:
        StartTime = time.monotonic()
        GetDataChange(DB,B_Bools=I_Bools,B_Bytes=I_bytes,B_int16=I_int16,B_int32=I_int32,B_Float=I_Float)
        if DataChange != {}:
            PublishRabbitMQ(PublishData = DataChange )
        StopTime = time.monotonic()
        TimeElapse = StopTime - StartTime