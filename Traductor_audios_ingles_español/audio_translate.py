from pydub import AudioSegment
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
import os

def transcribe_and_translate_audio(input_file, output_audio_file):
    """
    Function to transcribe audio to text, translate it and create a new audio file
    
    Parameters:
    input_file (str): Path to input MP3 file
    output_audio_file (str): Path to save the output Spanish audio file
    
    Returns:
    tuple: Original text, translated text
    """
    # Initialize recognizer and translator
    recognizer = sr.Recognizer()
    translator = Translator()
    
    # Convert mp3 to wav (speech_recognition needs wav format)
    try:
        audio = AudioSegment.from_mp3(input_file)
        wav_path = "temp.wav"
        audio.export(wav_path, format="wav")
        
        # Transcribe audio to text
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                # Transcribe to English text
                original_text = recognizer.recognize_google(audio_data)
                print("\nTranscripción original:", original_text)
                
                # Translate to Spanish
                translation = translator.translate(original_text, src='en', dest='es')
                spanish_text = translation.text
                print("\nTexto traducido:", spanish_text)
                
                # Create Spanish audio file
                tts = gTTS(text=spanish_text, lang='es')
                tts.save(output_audio_file)
                
                # Clean up temporary file
                os.remove(wav_path)
                
                return original_text, spanish_text
                
            except sr.UnknownValueError:
                print("No se pudo entender el audio")
                return None, None
            except sr.RequestError as e:
                print(f"Error en la solicitud al servicio de reconocimiento: {e}")
                return None, None
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        return None, None

def main():
    # Solicitar la ruta del archivo de audio al usuario
    print("\nTraductor de Audio (Inglés a Español)")
    print("-------------------------------------")
    print("Por favor, introduce la ruta completa del archivo de audio MP3")
    print("Ejemplo: C:/Users/nombre/Musica/audio.mp3")
    
    input_file = input("\nRuta del archivo MP3: ").strip()
    
    # Remover comillas si las hay
    input_file = input_file.strip('"\'')
    
    # Verificar si el archivo existe
    if not os.path.isfile(input_file):
        print(f"Error: No se encuentra el archivo: {input_file}")
        return
    
    # Crear la ruta de salida en el mismo directorio que el archivo de entrada
    nombre_base = os.path.splitext(input_file)[0]
    output_file = f"{nombre_base}_spanish.mp3"
    
    print(f"\nProcesando el archivo: {input_file}")
    print(f"El archivo traducido se guardará como: {output_file}")
    
    # Process the audio
    original, translated = transcribe_and_translate_audio(input_file, output_file)
    
    if original and translated:
        print("\nProceso completado con éxito:")
        print(f"Archivo de audio en español guardado como: {output_file}")
    else:
        print("\nOcurrió un error durante el proceso")

if __name__ == "__main__":
    main()