# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos del servidor y requisitos al contenedor
COPY server.py .
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 1102 para el servidor Snap7
EXPOSE 1102

# Comando para ejecutar el servidor
CMD ["python", "server.py"]
