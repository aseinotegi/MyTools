import csv
import pika

filename = "datosplisadora.csv"
QueueName = 'Pliadora'
RabbitIP = 'localhost'

# Verificar si el archivo ya existe
try:
    with open(filename) as f:
        pass
except FileNotFoundError:
    # Si el archivo no existe, crearlo y agregar el encabezado
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['DatosConsumidosDelRabbitMQ'])

# Conectar al servidor RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(RabbitIP))
channel = connection.channel()

# Asegurarnos de que la cola existe
channel.queue_declare(queue=QueueName, durable=True)

# Función de callback para procesar los mensajes recibidos
def callback(ch, method, properties, body):
    print("Recibido: %r" % body)

    # Abrir el archivo en modo de apéndice y agregar el mensaje recibido
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([body.decode()])

# Comenzar a consumir los mensajes
channel.basic_consume(queue=QueueName, on_message_callback=callback, auto_ack=True)

print('Esperando mensajes. Presione CTRL+C para salir.')

# Comenzar a consumir los mensajes en bucle
channel.start_consuming()
