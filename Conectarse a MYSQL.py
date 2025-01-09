import mysql.connector

# Configura la información de conexión
db_config = {
    "host": "54.210.79.222",  # Dirección IP de la instancia de Amazon
    "user": "vnode",
    "password": "vnode",
    "database": "vnode",  # Nombre de la base de datos
}

try:
    # Crea una conexión a la base de datos
    connection = mysql.connector.connect(**db_config)

    # Crea un cursor para ejecutar consultas
    cursor = connection.cursor()

    # Ejemplo: consulta a la tabla "plisadora"
    cursor.execute("SELECT * FROM test")

    # Recupera los resultados
    results = cursor.fetchall()

    # Haz algo con los resultados, por ejemplo, imprímelos
    for row in results:
        print(row)

except mysql.connector.Error as error:
    print(f"Error: {error}")

finally:
    # Cierra el cursor y la conexión
    if "connection" in locals():
        cursor.close()
        connection.close()
