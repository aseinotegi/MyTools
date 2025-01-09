import snap7
from datetime import datetime

IP = "192.168.10.2"
client = snap7.client.Client()
client.connect(IP, 0, 1)
Lenght = 1152
DB = 2501
def TimeStamp ():
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return timestamp_str 
while True:
    Bytedata = client.db_read(DB, 0,Lenght)
    Time = TimeStamp()
    print(Bytedata,Time)