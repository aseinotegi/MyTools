import subprocess
import whisper
from openai import OpenAI
import os

# Configuración de la clave de API de OpenAI
client = OpenAI(api_key="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")  # Cambia por tu clave


def verificar_rutas(video_path, audio_path, transcripcion_path, informe_path):
    """
    Verifica que las rutas de entrada y salida sean válidas.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"El archivo de video {video_path} no existe.")
    if os.path.exists(informe_path):
        print(f"El informe ya existe en {informe_path}. Será sobrescrito.")
    if os.path.exists(transcripcion_path):
        print(f"La transcripción ya existe en {transcripcion_path}. Se reutilizará.")
    if os.path.exists(audio_path):
        print(f"El archivo de audio ya existe en {audio_path}. Se reutilizará.")


def extraer_audio(video_path, audio_path):
    """
    Extrae el audio de un video utilizando ffmpeg si no existe ya el archivo de audio.
    """
    if os.path.exists(audio_path):
        print(f"El audio ya existe en {audio_path}. Se omite la extracción.")
        return
    ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"  # Ruta absoluta de ffmpeg
    command = [ffmpeg_path, "-i", video_path, "-q:a", "0", "-map", "a", audio_path]
    print(f"Ejecutando comando: {' '.join(command)}")
    subprocess.run(command, check=True)
    print(f"Audio extraído y guardado en {audio_path}")


def transcribir_audio(audio_path, transcripcion_path):
    """
    Transcribe el audio utilizando Whisper si no existe ya la transcripción.
    """
    if os.path.exists(transcripcion_path):
        print(f"La transcripción ya existe en {transcripcion_path}. Leyendo archivo...")
        with open(transcripcion_path, "r", encoding="utf-8") as f:
            transcripcion = f.read()
        print("Transcripción cargada desde el archivo.")
        return transcripcion

    print("Iniciando transcripción del audio...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcripcion = result["text"]

    # Guardar la transcripción en un archivo
    with open(transcripcion_path, "w", encoding="utf-8") as f:
        f.write(transcripcion)
    print(f"Transcripción completada y guardada en {transcripcion_path}")
    return transcripcion


def limpiar_transcripcion(transcripcion):
    """
    Elimina contenido irrelevante de la transcripción.
    """
    lineas = transcripcion.split("\n")
    lineas_utiles = [linea.strip() for linea in lineas if len(linea.split()) > 5]
    return "\n".join(lineas_utiles)


def dividir_transcripcion(transcripcion, max_tokens=1500):
    """
    Divide la transcripción en fragmentos de hasta 'max_tokens' tokens, respetando los límites de palabras.
    """
    palabras = transcripcion.split()
    fragmentos = []
    while palabras:
        fragmento = palabras[:max_tokens]
        palabras = palabras[max_tokens:]
        fragmentos.append(" ".join(fragmento))
    return fragmentos


def generar_resumen_y_desglose(transcripcion):
    """
    Genera un resumen breve y un desglose de los proyectos utilizando OpenAI.
    """
    fragmentos = dividir_transcripcion(transcripcion)
    resumen_total = ""
    desglose_total = ""

    for i, fragmento in enumerate(fragmentos):
        print(f"Procesando fragmento {i + 1} de {len(fragmentos)}...")

        # Generar resumen
        prompt_resumen = f"""
        Estás analizando la transcripción de una reunión de una startup dedicada a consultorías de IoT.
        Genera un resumen breve (uno o dos párrafos) que incluya los puntos clave discutidos.

        Transcripción:
        {fragmento}
        """
        try:
            response_resumen = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en resumir reuniones de proyectos de IoT."},
                    {"role": "user", "content": prompt_resumen}
                ],
                max_tokens=500
            )
            resumen_parcial = response_resumen.choices[0].message.content.strip()
            resumen_total += f"\n{resumen_parcial}\n"
        except Exception as e:
            print(f"Error al analizar el fragmento {i + 1} para el resumen: {e}")

        # Generar desglose
        prompt_desglose = f"""
        Estás analizando la transcripción de una reunión de una startup dedicada a consultorías de IoT. 
        En esta reunión, cada responsable de proyecto presenta el avance de su proyecto. 
        Tu tarea es resumir los puntos clave de cada proyecto de forma organizada y estructurada. 

        Para cada proyecto, identifica:
        1. El nombre o tema del proyecto (si no se menciona, indica 'Proyecto desconocido').
        2. Los avances realizados desde la última reunión.
        3. Los problemas encontrados o bloqueos.
        4. Las decisiones tomadas.
        5. Los próximos pasos a seguir.
        6. Cualquier otra información relevante.

        Presenta el resultado como una lista organizada y estructurada en este formato:

        - Proyecto: [nombre del proyecto]
          - Avances:
            - [avance 1]
            - [avance 2]
          - Problemas:
            - [problema 1]
            - [problema 2]
          - Decisiones tomadas:
            - [decisión 1]
            - [decisión 2]
          - Próximos pasos:
            - [paso 1]
            - [paso 2]
          - Información adicional:
            - [detalle 1]
            - [detalle 2]

        Transcripción:
        {fragmento}
        """
        try:
            response_desglose = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en desglosar reuniones de proyectos de IoT."},
                    {"role": "user", "content": prompt_desglose}
                ],
                max_tokens=1000
            )
            desglose_parcial = response_desglose.choices[0].message.content.strip()
            desglose_total += f"\n{desglose_parcial}\n"
        except Exception as e:
            print(f"Error al analizar el fragmento {i + 1} para el desglose: {e}")

    return resumen_total.strip(), desglose_total.strip()


def generar_informe_txt(video_path, audio_path, transcripcion_path, informe_path):
    """
    Genera un informe con el resumen y desglose de los proyectos y lo guarda en un archivo de texto plano.
    """
    try:
        verificar_rutas(video_path, audio_path, transcripcion_path, informe_path)

        # Extraer audio
        extraer_audio(video_path, audio_path)

        # Transcribir audio
        transcripcion = transcribir_audio(audio_path, transcripcion_path)
        if not transcripcion:
            print("No se pudo completar la transcripción. Proceso cancelado.")
            return

        # Limpiar transcripción
        transcripcion = limpiar_transcripcion(transcripcion)

        # Generar resumen y desglose
        resumen, desglose = generar_resumen_y_desglose(transcripcion)

        # Plantilla para el informe
        informe = f"""
        RESUMEN DE LA REUNIÓN
        =====================

        {resumen}

        ---------------------

        DESGLOSE DE PROYECTOS
        ======================

        {desglose}
        """

        # Guardar informe
        with open(informe_path, "w", encoding="utf-8") as f:
            f.write(informe)
        print(f"Informe generado y guardado en {informe_path}")
    except Exception as e:
        print(f"Error durante la generación del informe: {e}")


if __name__ == "__main__":
    # Rutas de entrada y salida
    video_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\iotinsights.mp4"
    audio_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\iotinsights.mp3"
    transcripcion_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\transcripcion.txt"
    informe_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\informe.txt"

    # Generar el informe
    generar_informe_txt(video_path, audio_path, transcripcion_path, informe_path)
