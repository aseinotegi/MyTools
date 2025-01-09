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
        # Detectar la edad en el frame capturado
        result = DeepFace.analyze(frame, actions=['age'], enforce_detection=False)

        # Imprimir el resultado para verificar su estructura
        print(result)

        # Verificar si el resultado contiene la edad
        if isinstance(result, list) and len(result) > 0 and 'age' in result[0]:
            age = result[0]['age']
        else:
            age = "No se detecta edad"
    except Exception as e:
        print("Error al analizar la imagen:", e)
        age = "Error"

    # Mostrar la edad en la ventana del video
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f'Edad: {age}', (50, 50), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow('Age Detection', frame)

    # Romper el bucle con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar todas las ventanas
cap.release()
cv2.destroyAllW
