# IMPORT LIBRARY
import snap7
from datetime import datetime
import struct
import pika

ChangeData = {}
ChangeData_mem = {}
client = 0

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

#CONNECT TO PLC
IP = "192.168.10.2"
client = snap7.client.Client()
client.connect(IP, 0, 1)


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



#GET TIMESTAMP
def TimeStamp ():
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return timestamp_str 

#READ DATA FROM PLC (BYTEARRAY)
def ReadFromPLC ():
    DB = 2501
    Bytedata = client.db_read(DB, 0,Lenght)
    return Bytedata

def GetAllDataPLC ():
    global ChangeData_mem
    AllData = {}
    if client.get_connected:
        PLCData = ReadFromPLC()
        if B_Bools > 0 :
            for _byte in range(StartBools,B_Bools):
                for _bit in range(8):
                    valor = get_bool(PLCData,_byte,_bit)
                    name = f'Bool_011_o_({_byte})_{_bit}'
                    AllData.update({name: valor})
        if B_Bytes > 0 :
            for _byte in range(StartBytes,B_Bytes):
                valor = get_byte(PLCData,_byte)
                name = f'Byte_011_o_({_byte})'
                AllData.update({name: valor})
        if B_Int16 > 0 :
            for _byte in range(StartInt16,StopInt16,2):
                valor = get_int16(PLCData,_byte)
                name = f'Int16_011_o_({_byte})'
                AllData.update({name: valor})   
        if B_Int32 > 0 :
            for _byte in range(StartInt32,StopInt32,4):
                valor = get_int32(PLCData,_byte)
                name = f'Int32_011_o_({_byte})'
                AllData.update({name: valor})   
        if B_Float > 0 :
            for _byte in range(StartFloat,StartFloat,4):
                valor = get_float(PLCData,_byte)
                name = f'Float_011_o_({_byte})'
                AllData.update({name: valor})
        TimeStamp_str = TimeStamp()
        AllData.update({"TimeStamp": TimeStamp_str})
        ChangeData_mem = AllData
        #print(AllData)
        return AllData 
def PublishRabbitMQ(PublishData):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.basic_publish(exchange='', routing_key='datos_plc', body=str(PublishData))

def GetChangeDataPLC ():
    ChangeData = {}
    if client.get_connected:
        ejecute = False 
        PLCData = ReadFromPLC()
        if B_Bools > 0 :
            for _byte in range(StartBools,StopBools):
                for _bit in range(8):
                    name = f'Bool_011_o_({_byte})_{_bit}'
                    valor = get_bool(PLCData, _byte, _bit)
                    if valor != ChangeData_mem[name]:
                        ChangeData.update({name: valor})
                        ChangeData_mem[name] = ChangeData[name]
                        ejecute = True
        if B_Bytes > 0 :
            for _byte in range(StartBytes,StopBytes):
                valor = get_byte(PLCData,_byte)
                name = f'Byte_011_o_({_byte})'
                if valor != ChangeData_mem[name]:
                        ChangeData.update({name: valor})
                        ChangeData_mem[name] = ChangeData[name]
                        ejecute = True
        if B_Int16 > 0 :
            for _byte in range(StartInt16,StopInt16,2):
                valor = get_int16(PLCData,_byte)
                name = f'Int16_011_o_({_byte})'
                if valor != ChangeData_mem[name]:
                        ChangeData.update({name: valor})
                        ChangeData_mem[name] = ChangeData[name]
                        ejecute = True
        if B_Int32 > 0 :
            for _byte in range(StartInt32,StopInt32,4):
                valor = get_int32(PLCData,_byte)
                name = f'Int32_011_o_({_byte})'
                if valor != ChangeData_mem[name]:
                        ChangeData.update({name: valor})
                        ChangeData_mem[name] = ChangeData[name]
                        ejecute = True
        if B_Float > 0 :
            for _byte in range(StartFloat,StopFloat,4):
                valor = get_float(PLCData,_byte)
                name = f'Float_011_o_({_byte})'
                if valor != ChangeData_mem[name]:
                        ChangeData.update({name: valor})
                        ChangeData_mem[name] = ChangeData[name]
                        ejecute = True
        if ejecute :                
            TimeStamp_str = TimeStamp()
            ChangeData.update({"TimeStamp": TimeStamp_str})
        if ChangeData != {}:
            PublishRabbitMQ(PublishData=ChangeData)
        #print(ChangeData)
        return ChangeData

FirstTime = False            
while True:
    if not FirstTime:
        GetAllDataPLC()
        FirstTime = True
    else:
        GetChangeDataPLC()

