import pika
from opcua import Client, ua

OPCData = ''

def read_input_value(node_id):
    global OPCData
    client_node = client.get_node(node_id)  # get node
    client_node_value = client_node.get_value()  # read node value
    print(str(client_node_value))
    OPCData = (str(client_node_value))
    return (str(client_node_value))

def PublishRabbitMQ(PublishData):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='datos_plc',durable=True)
    channel.basic_publish(exchange='', routing_key='datos_plc', body=str(PublishData))

client = Client("opc.tcp://192.168.0.1:4840")
client.connect()
root = client.get_root_node()
print("Objects root node is: ", root)

while True:
    read_input_value('ns=3;s="Top_secret"."S_Int"')
    PublishRabbitMQ(OPCData)

