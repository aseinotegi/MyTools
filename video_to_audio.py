from moviepy.editor import VideoFileClip
import os

def convertir_video_a_mp3(ruta_video, ruta_salida=None):
    """
    Convierte un archivo de video a formato MP3.
    """
    # Normalizar la ruta (maneja diferentes formatos de separadores)
    ruta_video = os.path.normpath(ruta_video)
    
    # Verificación explícita del archivo
    if not os.path.isfile(ruta_video):
        print(f"Error: No se encuentra el archivo: {ruta_video}")
        return None
        
    try:
        # Si no se especifica ruta de salida, crear una en el mismo directorio
        if ruta_salida is None:
            nombre_base = os.path.splitext(ruta_video)[0]
            ruta_salida = f"{nombre_base}.mp3"
        
        print(f"Iniciando la conversión del archivo: {ruta_video}")
        
        # Cargar el video
        video = VideoFileClip(ruta_video)
        
        # Verificar que el video tenga audio
        if video.audio is None:
            print("Error: El archivo de video no contiene audio")
            video.close()
            return None
            
        # Extraer el audio y guardarlo como MP3
        print("Extrayendo el audio...")
        video.audio.write_audiofile(ruta_salida)
        
        # Cerrar el archivo de video
        video.close()
        
        print(f"Conversión exitosa. Archivo MP3 guardado en: {ruta_salida}")
        return ruta_salida
        
    except Exception as e:
        print(f"Error durante la conversión: {str(e)}")
        return None

if __name__ == "__main__":
    # Solicitar la ruta del video al usuario
    print("\nConversor de Video a MP3")
    print("------------------------")
    print("Por favor, introduce la ruta completa del archivo de video INCLUIDA LA EXTENSION DEL VIDEO!!")
    print("Ejemplo: C:/Users/nombre/Videos/video.mkv")
    
    ruta_video = input("\nRuta del video: ").strip()
    
    # Si el usuario ingresa la ruta entre comillas, las removemos
    ruta_video = ruta_video.strip('"\'')
    
    # Intentar la conversión
    resultado = convertir_video_a_mp3(ruta_video)
    
    if resultado is None:
        print("La conversión no se pudo completar.")