import cv2
import os
from datetime import datetime

def capturar_imagen():
    """
    Accede a la cámara, muestra video en vivo y captura una imagen 
    cuando el usuario presiona la tecla 'espacio'.
    """
    # Inicializar la cámara (0 es generalmente la cámara integrada)
    camara = cv2.VideoCapture(0)
    
    # Verificar si la cámara se abrió correctamente
    if not camara.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return
    
    print("Cámara iniciada correctamente.")
    print("Presiona 'espacio' para capturar una imagen o 'q' para salir.")
    
    capturada = False
    
    while True:
        # Capturar frame por frame
        ret, frame = camara.read()
        
        # Si el frame se capturó correctamente
        if ret:
            # Mostrar el frame en una ventana
            cv2.imshow('Cámara - Presiona ESPACIO para capturar, Q para salir', frame)
            
            # Esperar por una tecla
            tecla = cv2.waitKey(1)
            
            # Si se presiona 'q', salir del bucle
            if tecla == ord('q'):
                print("Saliendo del programa...")
                break
            
            # Si se presiona 'espacio', guardar la imagen
            elif tecla == ord(' '):
                # Crear un nombre de archivo con la fecha y hora actual
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"captura_{timestamp}.jpg"
                
                # Crear directorio 'capturas' si no existe
                if not os.path.exists('capturas'):
                    os.makedirs('capturas')
                
                # Guardar la imagen
                ruta_completa = os.path.join('capturas', nombre_archivo)
                cv2.imwrite(ruta_completa, frame)
                
                print(f"Imagen guardada como: {ruta_completa}")
                capturada = True
        else:
            print("Error al capturar el frame.")
            break
    
    # Liberar la cámara y cerrar las ventanas
    camara.release()
    cv2.destroyAllWindows()
    
    return capturada

if _name_ == "_main_":
    capturar_imagen()