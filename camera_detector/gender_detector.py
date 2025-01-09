import cv2
from deepface import DeepFace

# Iniciar la captura de video desde la webcam
cap = cv2.VideoCapture(0)

while True:
    # Capturar frame por frame
    ret, frame = cap.read()

    if not ret:
        break

    try:
        # Detectar el género en el frame capturado
        result = DeepFace.analyze(frame, actions=['gender'], enforce_detection=False)

        # Imprimir el resultado para verificar su estructura
        print(result)

        # Verificar si el resultado contiene el género dominante
        if isinstance(result, list) and len(result) > 0 and 'dominant_gender' in result[0]:
            gender = result[0]['dominant_gender']
        else:
            gender = "No se detecta género"
    except Exception as e:
        print("Error al analizar la imagen:", e)
        gender = "Error"

    # Mostrar el género dominante en la ventana del video
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f'Género: {gender}', (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow('Gender Detection', frame)

    # Romper el bucle con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()
