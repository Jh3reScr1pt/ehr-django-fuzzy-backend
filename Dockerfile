# Usa una imagen base de Python
FROM python:3.10-slim

# Exponer el puerto de la aplicación
EXPOSE 8000

# Configura el directorio de trabajo
WORKDIR /app

# Copia solo el archivo de requisitos primero para aprovechar el cacheo
COPY requirements.txt /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el proyecto al contenedor
COPY . /app

# Comando para iniciar el servidor de desarrollo de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
