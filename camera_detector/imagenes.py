from mtcnn import MTCNN
import cv2

# Inicializar la cámara
cap = cv2.VideoCapture(0)

# Inicializar MTCNN
detector = MTCNN()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Realizar la detección de caras
    faces = detector.detect_faces(frame)

    # Dibujar las detecciones en la imagen
    for face in faces:
        (x, y, w, h) = face['box']
        confidence = face['confidence']
        keypoints = face['keypoints']

        # Dibujar el cuadro alrededor de la cara
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Añadir la confianza de detección
        cv2.putText(frame, f"Conf: {confidence:.2f}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Dibujar los puntos clave
        cv2.circle(frame, (keypoints['left_eye']), 2, (0, 255, 0), 2)
        cv2.circle(frame, (keypoints['right_eye']), 2, (0, 255, 0), 2)
        cv2.circle(frame, (keypoints['nose']), 2, (0, 255, 0), 2)
        cv2.circle(frame, (keypoints['mouth_left']), 2, (0, 255, 0), 2)
        cv2.circle(frame, (keypoints['mouth_right']), 2, (0, 255, 0), 2)

    # Mostrar la imagen con las detecciones
    cv2.imshow('MTCNN Detección de Caras', frame)

    # Romper el bucle con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar los recursos
cap.release()
cv2.destroyAllWindows()
