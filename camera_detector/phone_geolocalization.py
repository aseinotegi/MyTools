import phonenumbers
import requests

def geolocalizar_telefono(numero_telefono):
    try:
        # Analizar el número de teléfono
        telefono = phonenumbers.parse(numero_telefono, None)
        
        # Validar el número de teléfono
        if not phonenumbers.is_valid_number(telefono):
            return "Número de teléfono no válido."
        
        # Obtener el país del número de teléfono
        region_code = phonenumbers.region_code_for_number(telefono)
        
        # Usar la API de geolocalización para obtener coordenadas
        api_key = 'df64e8957a1c4a6292274a49f0d14607'
        url = f"https://api.opencagedata.com/geocode/v1/json?q={region_code}&key={api_key}"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and data['results']:
            location = data['results'][0]['geometry']
            return location
        else:
            return "No se pudo obtener la geolocalización."
    
    except phonenumbers.phonenumberutil.NumberParseException:
        return "Número de teléfono no válido."

# Ejemplo de uso
numero_telefono = "+34657794433"  # Reemplaza con el número de teléfono que quieres geolocalizar
ubicacion = geolocalizar_telefono(numero_telefono)
print(ubicacion)
