import cv2
from deepface import DeepFace
from mtcnn import MTCNN
import tensorflow as tf
import datetime
import os

# Desactivar mensajes de información de TensorFlow
tf.get_logger().setLevel('ERROR')

# Iniciar la captura de video desde la webcam
cap = cv2.VideoCapture(0)

# Crear el detector MTCNN con parámetros personalizados
detector = MTCNN(min_face_size=40, steps_threshold=[0.6, 0.7, 0.7], scale_factor=0.709)

def save_image_with_info(frame, num_faces, dominant_genders, dominant_races, ages):
    # Crear el nombre del archivo basado en la hora actual
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.jpg"
    filepath = os.path.join(os.getcwd(), filename)
    
    # Dibujar la información en la imagen
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1

    cv2.putText(frame, f'Personas: {num_faces}', (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    for i, (gender, race, age) in enumerate(zip(dominant_genders, dominant_races, ages)):
        text = f'Género: {gender}, Raza: {race}, Edad: {age}'
        cv2.putText(frame, text, (10, 60 + 20 * i), font, font_scale, (255, 0, 0), font_thickness, cv2.LINE_AA)
    
    # Guardar la imagen
    success = cv2.imwrite(filepath, frame)
    if success:
        print(f"Imagen guardada como {filepath}")
    else:
        print(f"Error al guardar la imagen en {filepath}")

while True:
    # Capturar frame por frame
    ret, frame = cap.read()

    if not ret:
        break

    try:
        # Detectar rostros en el frame capturado usando MTCNN
        results = detector.detect_faces(frame)
        num_faces = len(results)
        
        # Inicializar listas para los detalles de cada rostro
        dominant_genders = []
        dominant_races = []
        ages = []

        for result in results:
            bounding_box = result['box']
            face = frame[bounding_box[1]:bounding_box[1] + bounding_box[3], bounding_box[0]:bounding_box[0] + bounding_box[2]]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)

            # Analizar atributos de cada rostro
            analysis = DeepFace.analyze(face, actions=['gender', 'race', 'age'], enforce_detection=False)
            print(f'Analysis result: {analysis}')  # Agregar depuración

            # Validar y agregar resultados a las listas
            if isinstance(analysis, list) and len(analysis) > 0 and isinstance(analysis[0], dict):
                dominant_genders.append(analysis[0].get('dominant_gender', 'Desconocido'))
                dominant_races.append(analysis[0].get('dominant_race', 'Desconocido'))
                ages.append(analysis[0].get('age', 'Desconocido'))

        # Si se detectan más de una persona, guardar la imagen con la información
        if num_faces > 1:
            save_image_with_info(frame.copy(), num_faces, dominant_genders, dominant_races, ages)

    except Exception as e:
        print("Error al analizar la imagen:", e)
        num_faces = 0
        dominant_genders = []
        dominant_races = []
        ages = []

    # Mostrar el número de personas y sus atributos en la ventana del video
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5  # Reducir el tamaño del texto
    font_thickness = 1  # Reducir el grosor del texto

    cv2.putText(frame, f'Personas: {num_faces}', (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    for i, result in enumerate(results):
        bounding_box = result['box']
        cv2.rectangle(frame,
                      (bounding_box[0], bounding_box[1]),
                      (bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]),
                      (0, 255, 0), 2)
        if i < len(dominant_genders):
            cv2.putText(frame, f'Género: {dominant_genders[i]}', (bounding_box[0], bounding_box[1] - 30), font, font_scale, (255, 0, 0), font_thickness, cv2.LINE_AA)
        if i < len(dominant_races):
            cv2.putText(frame, f'Raza: {dominant_races[i]}', (bounding_box[0], bounding_box[1] - 10), font, font_scale, (255, 0, 0), font_thickness, cv2.LINE_AA)
        if i < len(ages):
            cv2.putText(frame, f'Edad: {ages[i]}', (bounding_box[0], bounding_box[1] + bounding_box[3] + 20), font, font_scale, (255, 0, 0), font_thickness, cv2.LINE_AA)

    cv2.imshow('People Detection and Analysis', frame)

    # Romper el bucle con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()
