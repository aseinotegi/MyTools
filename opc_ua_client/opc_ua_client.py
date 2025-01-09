import os
import asyncio
from asyncua import Client, ua
import datetime
from typing import List, Dict, Any


def read_node_ids(file_path: str) -> List[str]:
    """
    Lee los Node IDs desde un archivo de texto.

    Args:
        file_path: Ruta del archivo que contiene los Node IDs.

    Returns:
        Una lista de Node IDs.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo '{file_path}' no existe. Crea un archivo con los Node IDs.")

    with open(file_path, 'r') as f:
        # Leer líneas y eliminar espacios en blanco
        node_ids = [line.strip() for line in f if line.strip()]
    
    if not node_ids:
        raise ValueError(f"El archivo '{file_path}' está vacío. Agrega Node IDs válidos.")

    return node_ids


async def explore_node(node, file):
    """
    Explora un nodo y sus hijos recursivamente, escribiendo solo Node IDs válidos en un archivo.

    Args:
        node: Nodo actual que se está explorando.
        file: Archivo donde se escriben los resultados.
    """
    try:
        # Leer Node ID
        node_id = node.nodeid.to_string()

        # Filtrar solo los nodos con identificadores válidos en formato ns=X;s=...
        if "ns=" in node_id and ";s=" in node_id:
            file.write(f"{node_id}\n")  # Guardar en formato para nodes.txt

        # Obtener los hijos del nodo y explorar recursivamente
        children = await node.get_children()
        for child in children:
            await explore_node(child, file)
    except Exception as e:
        file.write(f"# Error explorando nodo: {e}\n")  # Comentario con el error en el archivo


async def browse_server(url: str, username: str = None, password: str = None, security_mode: str = "None"):
    """
    Realiza un browse recursivo en el servidor OPC UA y exporta los Node IDs en formato para nodes.txt.

    Args:
        url: URL del servidor OPC UA.
        username: Nombre de usuario para autenticación (opcional).
        password: Contraseña para autenticación (opcional).
        security_mode: Nivel de seguridad (por defecto "None").
    """
    client = Client(url=url)
    output_file = "server_browse.txt"
    
    try:
        # Configurar cliente
        if username and password:
            client.set_user(username)
            client.set_password(password)
        if security_mode != "None":
            await client.set_security_string(security_mode)

        # Conectar al servidor
        await client.connect()
        print(f"Explorando el servidor OPC UA en {url}...\n")
        
        # Obtener el nodo raíz
        root = client.nodes.root

        # Abrir archivo para escribir resultados
        with open(output_file, 'w') as f:
            f.write("# Exploración recursiva del servidor OPC UA (formato nodes.txt):\n")
            
            # Explorar el nodo raíz recursivamente
            await explore_node(root, f)

        print(f"Exploración completada. Resultados guardados en '{output_file}'.")
    except Exception as e:
        print(f"Error durante la exploración: {e}")
    finally:
        await client.disconnect()


class DataChangeHandler:
    def __init__(self, logger):
        self.logger = logger

    async def datachange_notification(self, node, value, data):
        """
        Método que se llama cuando se detecta un cambio de valor en un nodo.
        """
        await self.logger.handle_value_change(node, value)


class OPCUADataLogger:
    def __init__(self, url: str, nodes: list, log_file: str, username: str = None, password: str = None, security_mode: str = "None"):
        self.url = url
        self.nodes = nodes
        self.log_file = os.path.join(os.getcwd(), log_file)
        self.username = username
        self.password = password
        self.security_mode = security_mode
        self.last_values: Dict[str, Any] = {}

    async def log_value_change(self, node_id: str, value: Any):
        """
        Registra un cambio de valor en el archivo de log.
        """
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("Timestamp | Node | Valor\n")

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        log_entry = f"{timestamp} | Node: {node_id} | Valor: {value}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)

    async def handle_value_change(self, node, value):
        """
        Maneja los cambios de valor en un nodo.
        """
        node_id = node.nodeid.to_string()
        
        if node_id not in self.last_values or self.last_values[node_id] != str(value):
            self.last_values[node_id] = str(value)
            await self.log_value_change(node_id, value)

    async def subscribe_to_nodes(self, client):
        """
        Suscribe a los nodos para monitorear cambios.
        """
        handler = DataChangeHandler(self)
        subscription = await client.create_subscription(50, handler)
        
        for node_id in self.nodes:
            try:
                node = client.get_node(node_id)

                # Validar si el nodo tiene el atributo Value (es un nodo de tipo Variable)
                node_class = await node.read_node_class()
                if node_class != ua.NodeClass.Variable:
                    print(f"El nodo {node_id} no es de tipo Variable. Ignorando...")
                    continue

                await subscription.subscribe_data_change(node)
            except Exception as e:
                print(f"Error suscribiéndose al nodo {node_id}: {e}")
            
        return subscription

    async def configure_client(self, client):
        """
        Configura el cliente OPC UA con las credenciales y el nivel de seguridad.
        """
        if self.username and self.password:
            client.set_user(self.username)
            client.set_password(self.password)
            
        # Configurar seguridad solo si no es "None"
        if self.security_mode != "None":
            try:
                await client.set_security_string(self.security_mode)
            except Exception as e:
                print(f"Error configurando el nivel de seguridad: {e}")

    async def run(self):
        """
        Ejecuta el cliente OPC UA y monitorea los nodos.
        """
        client = Client(url=self.url)
        
        try:
            await self.configure_client(client)
            await client.connect()
            await self.subscribe_to_nodes(client)
            print(f"Cliente conectado a {self.url}")
            
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error de conexión: {e}")
        finally:
            await client.disconnect()
            print("Cliente desconectado")


if __name__ == "__main__":
    SERVER_URL = "opc.tcp://192.168.1.134:4840"
    SECURITY_MODE = "None"  # Sin seguridad
    NODES_FILE = "nodes.txt"
    LOG_FILE = "cambios_variables.txt"
    USERNAME = "as"
    PASSWORD = "as"

    print("¿Deseas explorar las variables disponibles en el servidor OPC UA? (y/n)")
    choice = input().strip().lower()

    if choice == "y":
        asyncio.run(browse_server(SERVER_URL, USERNAME, PASSWORD, SECURITY_MODE))
    else:
        try:
            NODE_IDS = read_node_ids(NODES_FILE)
            print(f"Nodos cargados: {NODE_IDS}")
        except (FileNotFoundError, ValueError) as e:
            print(f"Error al leer los Node IDs: {e}")
            exit(1)

        logger = OPCUADataLogger(
            url=SERVER_URL,
            nodes=NODE_IDS,
            log_file=LOG_FILE,
            username=USERNAME,
            password=PASSWORD,
            security_mode=SECURITY_MODE
        )

        try:
            asyncio.run(logger.run())
        except KeyboardInterrupt:
            print("\nDetención del cliente solicitada por el usuario")
