import paho.mqtt.client as mqtt
import json
import time

# Datos a introducir con las variables de plant
data = {
    "data1": "1",
    "data2": "2",
    "data3": "3"
}

previous_data = {}

# Mostrar conexión
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado al broker MQTT")
    else:
        print(f"Error de conexión, código {rc}")

# Detectar cambios en los datos
def detect_changes(current_data, previous_data):
    changes = {}
    for key in current_data:
        if current_data[key] != previous_data.get(key):
            changes[key] = current_data[key]
    return changes

# Crear instancia del cliente
client = mqtt.Client()

# Asignar la función de conexión
client.on_connect = on_connect

# Conectar al broker
client.connect("121.11.244.11", 1883, 60)

# Iniciar el bucle del cliente
client.loop_start()

try:
    while True:
        if not previous_data:
            # Inicializar previous_data con data la primera vez
            previous_data = data.copy()
            print("Inicializando previous_data con los valores actuales de data.")
        
        # Detectar y publicar solo los cambios
        changes = detect_changes(data, previous_data)
        if changes:
            client.publish("script", json.dumps(changes))
            print(f"Publicado cambio: {changes}")
            # Actualizar previous_data para reflejar los cambios actuales
            previous_data = data.copy()
            
        # Simular cambios en data para probar el script
        # Esta parte debería ser reemplazada con la lógica para actualizar `data` externamente
        data["data1"] = str(int(data["data1"]) + 1 if int(data["data1"]) < 10 else 1)
        data["data2"] = str(int(data["data2"]) + 1 if int(data["data2"]) < 10 else 2)
        data["data3"] = str(int(data["data3"]) + 1 if int(data["data3"]) < 10 else 3)
        
        # Esperar un poco antes de la próxima verificación
        time.sleep(5)

except KeyboardInterrupt:
    print("Publicación interrumpida")

# Finalizar conexión
client.loop_stop()
client.disconnect()