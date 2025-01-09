import csv
import pika
import sys
import logging
from typing import Optional

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    def __init__(self, host: str, queue_name: str, output_file: str):
        self.host = host
        self.queue_name = queue_name
        self.output_file = output_file
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None

    def setup_csv(self):
        """Inicializa el archivo CSV si no existe"""
        try:
            with open(self.output_file, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['DatosConsumidosDelRabbitMQ', 'Timestamp'])
                logger.info(f"Archivo CSV creado: {self.output_file}")
        except FileExistsError:
            logger.info(f"El archivo CSV ya existe: {self.output_file}")

    def connect(self):
        """Establece la conexión con RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                username='admin',  # Reemplaza con tu usuario
                password='admin'  # Reemplaza con tu contraseña
            )
            
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            logger.info(f"Conectado a RabbitMQ en {self.host}")
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Error al conectar a RabbitMQ: {e}")
            sys.exit(1)

    def callback(self, ch, method, properties, body):
        """Procesa los mensajes recibidos"""
        try:
            mensaje = body.decode('utf-8')
            #logger.info(f"Mensaje recibido: {mensaje}")
            
            with open(self.output_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([mensaje])
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        """Inicia el consumo de mensajes"""
        try:
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback
            )
            
            logger.info(f"Esperando mensajes de la cola '{self.queue_name}'. CTRL+C para salir.")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Cerrando consumidor...")
            if self.channel:
                self.channel.stop_consuming()
            self.close()
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            self.close()

    def close(self):
        """Cierra la conexión con RabbitMQ"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Conexión cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar la conexión: {e}")

def main():
    consumer = RabbitMQConsumer(
        host='192.168.1.134',
        queue_name='Codesys',
        output_file='Datos_codesys.csv'
    )
    
    consumer.setup_csv()
    consumer.connect()
    consumer.start_consuming()

if __name__ == '__main__':
    main()