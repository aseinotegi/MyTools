import subprocess
import whisper
from openai import OpenAI
import os
import spacy
from transformers import pipeline
from temas_clave import TEMAS_CLAVE

from dotenv import load_dotenv

load_dotenv()  # CREA EL .ENV PARA IMPORTAR LA KEY
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Cargar modelo de spaCy
nlp = spacy.load("es_core_news_md")  # Cambia a "en_core_web_md" si el idioma es inglés

# Cargar modelo de transformers para clasificación de temas
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def extraer_audio(video_path, audio_path):
    """
    Extrae el audio de un video utilizando ffmpeg si no existe ya el archivo de audio.
    """
    if os.path.exists(audio_path):
        print(f"El audio ya existe en {audio_path}. Se omite la extracción.")
        return
    if not os.path.exists(video_path):
        print(f"El archivo de video {video_path} no existe. Proceso cancelado.")
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

    if not os.path.exists(audio_path):
        print(f"El archivo de audio {audio_path} no existe. Proceso cancelado.")
        return

    print("Iniciando transcripción del audio...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcripcion = result["text"]

    # Guardar la transcripción en un archivo
    with open(transcripcion_path, "w", encoding="utf-8") as f:
        f.write(transcripcion)
    print(f"Transcripción completada y guardada en {transcripcion_path}")
    return transcripcion


def limpiar_y_enriquecer_transcripcion(transcripcion, enriched_path):
    """
    Limpia y enriquece la transcripción utilizando spaCy y transformers. Guarda el texto enriquecido.
    """
    # Verificar si ya existe la transcripción enriquecida
    if os.path.exists(enriched_path):
        print(f"La transcripción enriquecida ya existe en {enriched_path}. Leyendo archivo...")
        with open(enriched_path, "r", encoding="utf-8") as f:
            transcripcion_limpia = f.read()
        print("Transcripción enriquecida cargada desde el archivo.")
        return transcripcion_limpia

    print("Iniciando limpieza y enriquecimiento de datos...")
    doc = nlp(transcripcion)

    # Filtrar frases relevantes (longitud mínima)
    frases_relevantes = [sent.text for sent in doc.sents if len(sent.text.split()) > 5]

    # Extraer entidades nombradas (proyectos, problemas, etc.)
    entidades = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PROJ", "MISC", "LOC"]]
    print(f"Entidades detectadas: {entidades}")

    # Clasificación de temas utilizando transformers
    temas_clave = classifier(
        transcripcion,
        candidate_labels=TEMAS_CLAVE,
        multi_label=True
    )
    print(f"Temas clave detectados: {temas_clave['labels']}")

    # Reconstruir una transcripción más limpia y relevante
    transcripcion_limpia = "\n".join(frases_relevantes)

    # Guardar la transcripción enriquecida en un archivo
    with open(enriched_path, "w", encoding="utf-8") as f:
        f.write(transcripcion_limpia)
    print(f"Transcripción enriquecida guardada en {enriched_path}")
    return transcripcion_limpia


def generar_resumen_y_desglose(transcripcion):
    """
    Genera un resumen breve y un desglose de los proyectos utilizando OpenAI.
    """
    # Generar resumen
    prompt_resumen = f"""
    Genera un resumen breve basado en la siguiente transcripción:
    {transcripcion}
    """
    response_resumen = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en resumir reuniones de proyectos de IoT."},
            {"role": "user", "content": prompt_resumen}
        ],
        max_tokens=500
    )
    resumen = response_resumen.choices[0].message.content.strip()

    # Generar desglose
    prompt_desglose = f"""
    Desglosa los puntos clave de cada proyecto detectado en la reunión según los temas:
    {transcripcion}.
    """
    response_desglose = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente experto en desglosar reuniones de proyectos de IoT."},
            {"role": "user", "content": prompt_desglose}
        ],
        max_tokens=1000
    )
    desglose = response_desglose.choices[0].message.content.strip()

    return resumen, desglose


def generar_informe_txt(video_path, audio_path, transcripcion_path, enriched_path, informe_path):
    """
    Genera un informe con el resumen y desglose de los proyectos y lo guarda en un archivo de texto plano.
    """
    # Extraer audio
    extraer_audio(video_path, audio_path)

    # Transcribir audio
    transcripcion = transcribir_audio(audio_path, transcripcion_path)
    if not transcripcion:
        print("No se pudo completar la transcripción. Proceso cancelado.")
        return

    # Limpiar y enriquecer transcripción
    transcripcion_limpia = limpiar_y_enriquecer_transcripcion(transcripcion, enriched_path)

    # Generar resumen y desglose
    resumen, desglose = generar_resumen_y_desglose(transcripcion_limpia)

    # Guardar el informe en un archivo de texto
    informe = f"""
    RESUMEN DE LA REUNIÓN
    =====================

    {resumen}

    ---------------------

    DESGLOSE DE PROYECTOS
    ======================

    {desglose}
    """
    with open(informe_path, "w", encoding="utf-8") as f:
        f.write(informe)
    print(f"Informe generado y guardado en {informe_path}")


if __name__ == "__main__":
    # Rutas de entrada y salida
    video_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\iotinsights.mp4"
    audio_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\iotinsights.mp3"
    transcripcion_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\transcripcion.txt"
    enriched_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\enriched_transcripcion.txt"
    informe_path = "C:\\Users\\AnderSein\\Videos\\transcripcion\\informe.txt"

    # Generar el informe
    generar_informe_txt(video_path, audio_path, transcripcion_path, enriched_path, informe_path)
