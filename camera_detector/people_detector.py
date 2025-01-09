import cv2
from deepface import DeepFace
from mtcnn import MTCNN
import tensorflow as tf

# Desactivar mensajes de información de TensorFlow
tf.get_logger().setLevel('ERROR')

# Iniciar la captura de video desde la webcam
cap = cv2.VideoCapture(0)

# Crear el detector MTCNN con parámetros personalizados
detector = MTCNN(min_face_size=40, steps_threshold=[0.6, 0.7, 0.7], scale_factor=0.709)

while True:
    # Capturar frame por frame
    ret, frame = cap.read()

    if not ret:
        break

    try:
        # Detectar rostros en el frame capturado usando MTCNN
        results = detector.detect_faces(frame)
        num_faces = len(results)
        
    except Exception as e:
        print("Error al analizar la imagen:", e)
        num_faces = 0

    # Mostrar el número de personas en la ventana del video
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f'Personas: {num_faces}', (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Dibujar los cuadros alrededor de los rostros detectados
    for result in results:
        bounding_box = result['box']
        cv2.rectangle(frame,
                      (bounding_box[0], bounding_box[1]),
                      (bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]),
                      (0, 255, 0), 2)

    cv2.imshow('People Detection', frame)

    # Romper el bucle con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()
