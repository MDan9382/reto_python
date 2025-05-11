import cv2
import os
import numpy as np
import requests
import json
from datetime import datetime

# Configuración de Azure Computer Vision
# Necesitarás configurar estas variables con tus propias credenciales de Azure
VISION_ENDPOINT = ""  # Por ejemplo: "https://tu-resource.cognitiveservices.azure.com/"
VISION_KEY = ""          # Clave de suscripción de Azure Vision

def detectar_personas_azure(imagen_path):
    """
    Detecta personas en una imagen utilizando Azure Computer Vision API
    
    Args:
        imagen_path: Ruta al archivo de imagen a analizar
        
    Returns:
        bool: True si se detectó al menos una persona, False en caso contrario
        int: Número de personas detectadas
        imagen: Imagen con las detecciones marcadas
    """
    # Cargar la imagen para procesamiento local
    imagen = cv2.imread(imagen_path)
    if imagen is None:
        print(f"Error al cargar la imagen: {imagen_path}")
        return False, 0, None
    
    # Preparar la solicitud a Azure Vision
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': VISION_KEY
    }
    
    # Parámetros para la API de Azure Vision
    params = {
        'visualFeatures': 'Objects',  # Detectar objetos, que incluye personas
        'language': 'es',
        'detectOrientation': 'true'
    }
    
    api_url = f"{VISION_ENDPOINT}/vision/v3.2/analyze"
    
    # Leer la imagen como bytes para enviarla a la API
    with open(imagen_path, 'rb') as image_data:
        image_bytes = image_data.read()
    
    try:
        # Realizar la solicitud a Azure
        response = requests.post(
            api_url,
            headers=headers,
            params=params,
            data=image_bytes
        )
        response.raise_for_status()  # Verificar si hay errores HTTP
        
        # Procesar la respuesta
        analysis = response.json()
        
        # Crear una copia de la imagen para dibujar los resultados
        imagen_con_detecciones = imagen.copy()
        
        # Contar personas y dibujar cajas alrededor de ellas
        personas_detectadas = []
        
        if 'objects' in analysis:
            for objeto in analysis['objects']:
                if objeto['object'].lower() in ['person', 'persona', 'people', 'personas', 'human', 'humano']:
                    # Obtener coordenadas del rectángulo
                    rect = objeto['rectangle']
                    x = rect['x']
                    y = rect['y']
                    w = rect['w']
                    h = rect['h']
                    
                    # Agregar a la lista de personas
                    personas_detectadas.append((x, y, w, h))
                    
                    # Dibujar rectángulo
                    cv2.rectangle(imagen_con_detecciones, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Agregar etiqueta con confianza
                    confianza = objeto['confidence']
                    etiqueta = f"Persona: {confianza:.2f}"
                    cv2.putText(imagen_con_detecciones, etiqueta, (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Determinar si se encontraron personas
        hay_personas = len(personas_detectadas) > 0
        num_personas = len(personas_detectadas)
        
        # Agregar texto con la información de detección
        if hay_personas:
            texto = f"Personas detectadas: {num_personas}"
            cv2.putText(imagen_con_detecciones, texto, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(imagen_con_detecciones, "No se detectaron personas", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        return hay_personas, num_personas, imagen_con_detecciones
        
    except Exception as e:
        print(f"Error al conectar con Azure Vision API: {str(e)}")
        return False, 0, imagen  # Devolver la imagen original en caso de error

def capturar_imagen():
    """
    Accede a la cámara, muestra video en vivo y captura una imagen 
    cuando el usuario presiona la tecla 'espacio'. Después analiza si hay personas
    usando Azure Vision Studio.
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
            
            # Si se presiona 'espacio', guardar la imagen y analizar
            elif tecla == ord(' '):
                # Crear un nombre de archivo con la fecha y hora actual
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"captura_{timestamp}.jpg"
                
                # Crear directorio 'capturas' si no existe
                if not os.path.exists('capturas'):
                    os.makedirs('capturas')
                
                # Guardar la imagen original
                ruta_completa = os.path.join('capturas', nombre_archivo)
                cv2.imwrite(ruta_completa, frame)
                print(f"Imagen guardada como: {ruta_completa}")
                
                # Detectar personas en la imagen usando Azure Vision
                print("Analizando imagen con Azure Vision Studio...")
                hay_personas, num_personas, imagen_analizada = detectar_personas_azure(ruta_completa)
                
                # Mostrar los resultados
                if hay_personas:
                    print(f"Se detectaron {num_personas} personas en la imagen")
                else:
                    print("No se detectaron personas en la imagen")
                
                # Guardar la imagen analizada
                nombre_analisis = f"analisis_{timestamp}.jpg"
                ruta_analisis = os.path.join('capturas', nombre_analisis)
                cv2.imwrite(ruta_analisis, imagen_analizada)
                print(f"Imagen con análisis guardada como: {ruta_analisis}")
                
                # Mostrar la imagen analizada
                cv2.imshow('Análisis de personas con Azure', imagen_analizada)
                
                capturada = True
        else:
            print("Error al capturar el frame.")
            break
    
    # Liberar la cámara y cerrar las ventanas
    camara.release()
    cv2.destroyAllWindows()
    
    return capturada

def analizar_imagen_existente(ruta_imagen):
    """
    Analiza una imagen existente para detectar personas usando Azure Vision Studio
    
    Args:
        ruta_imagen: Ruta al archivo de imagen a analizar
    """
    # Verificar si la imagen existe
    if not os.path.exists(ruta_imagen):
        print(f"Error: No se encontró la imagen en {ruta_imagen}")
        return
    
    # Detectar personas usando Azure Vision
    print(f"Analizando imagen con Azure Vision Studio: {ruta_imagen} ...")
    hay_personas, num_personas, imagen_analizada = detectar_personas_azure(ruta_imagen)
    
    # Mostrar resultados
    if hay_personas:
        print(f"Se detectaron {num_personas} personas en la imagen")
    else:
        print("No se detectaron personas en la imagen")
    
    # Guardar la imagen analizada
    directorio, nombre_archivo = os.path.split(ruta_imagen)
    base_nombre, extension = os.path.splitext(nombre_archivo)
    nombre_analisis = f"{base_nombre}_analisis{extension}"
    
    # Crear directorio 'analisis' si no existe
    if not os.path.exists('analisis'):
        os.makedirs('analisis')
    
    ruta_analisis = os.path.join('analisis', nombre_analisis)
    cv2.imwrite(ruta_analisis, imagen_analizada)
    print(f"Imagen con análisis guardada como: {ruta_analisis}")
    
    # Mostrar la imagen
    cv2.imshow('Análisis de personas con Azure', imagen_analizada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def verificar_configuracion_azure():
    """
    Verifica que las credenciales de Azure estén configuradas
    """
    if VISION_ENDPOINT == "TU_ENDPOINT_DE_AZURE_VISION" or VISION_KEY == "TU_CLAVE_DE_AZURE_VISION":
        print("\n" + "=" * 80)
        print("ATENCIÓN: Es necesario configurar las credenciales de Azure Vision Studio")
        print("1. Crea una cuenta en Azure y un recurso de Computer Vision")
        print("2. Obtén el endpoint y la clave de API")
        print("3. Actualiza las variables VISION_ENDPOINT y VISION_KEY en este script")
        print("=" * 80 + "\n")
        return False
    return True

if __name__ == "__main__":
    # Verificar configuración de Azure
    if not verificar_configuracion_azure():
        print("Ejecutando en modo de demostración (sin conexión a Azure)")
    
    # Si se proporciona un argumento, analizar la imagen especificada
    import sys
    
    if len(sys.argv) > 1:
        ruta_imagen = sys.argv[1]
        analizar_imagen_existente(ruta_imagen)
    else:
        # Si no hay argumentos, iniciar la captura de cámara
        capturar_imagen()