import os
import shutil

def organize_downloads(downloads_folder):
    if not os.path.exists(downloads_folder):
        print(f'No se encontró la carpeta de descargas en {downloads_folder}')
        return

    # Definición de categorías y extensiones
    categories = {
        'Documentos': ['.DOC', '.DOCX', '.PDF', '.TXT', '.ODT', '.RTF', '.EPUB'],
        'Imágenes': ['.JPG', '.JPEG', '.PNG', '.GIF', '.BMP', '.TIFF', '.SVG'],
        'Videos': ['.MP4', '.MKV', '.AVI', '.MOV', '.WMV', '.FLV', '.WEBM'],
        'Audio': ['.MP3', '.WAV', '.FLAC', '.AAC', '.OGG', '.M4A'],
        'Comprimidos': ['.ZIP', '.RAR', '.7Z', '.TAR', '.GZ'],
        'Software': ['.EXE', '.MSI', '.DMG', '.ISO'],
        'Hojas de Cálculo': ['.XLS', '.XLSX', '.CSV', '.ODS'],
        'Presentaciones': ['.PPT', '.PPTX', '.KEY', '.ODP'],
        'Código y Scripts': ['.PY', '.JS', '.HTML', '.CSS', '.JAVA', '.C', '.CPP', '.CS', '.RB', '.GO', '.PHP'],
        'Libros y Manuales': ['.PDF', '.EPUB', '.MOBI'],
        'Otros': []
    }

    # Crear subcarpetas y mover archivos
    for root, dirs, files in os.walk(downloads_folder):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[-1].upper()

            # Encontrar la categoría
            destination_folder = None
            for category, extensions in categories.items():
                if file_extension in extensions:
                    destination_folder = os.path.join(downloads_folder, category)
                    break
            if not destination_folder:
                destination_folder = os.path.join(downloads_folder, 'Otros')

            # Crear la carpeta de destino si no existe
            os.makedirs(destination_folder, exist_ok=True)

            # Mover archivo
            try:
                shutil.move(file_path, os.path.join(destination_folder, file))
                print(f'Movido: {file} -> {destination_folder}')
            except Exception as e:
                print(f'Error al mover {file}: {e}')

def main():
    # Cambia esta ruta a la de tu carpeta de descargas
    downloads_path = os.path.expanduser('~/Downloads')  # Uso del directorio predeterminado
    organize_downloads(downloads_path)

if __name__ == "__main__":
    main()
