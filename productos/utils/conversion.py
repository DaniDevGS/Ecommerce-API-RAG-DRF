import requests
import logging


logger = logging.getLogger(__name__)

def obtener_cambio():
    API_URL = "https://v6.exchangerate-api.com/v6/37de8ccc33411893bb7d71ba/latest/USD"
    try:
        response = requests.get(API_URL, timeout=5) 
        response.raise_for_status() 
        data = response.json()
        
        if 'conversion_rates' in data and 'VES' in data['conversion_rates']:
            # *** ESTA LÍNEA RETORNA EL PRECIO DEL BOLÍVAR (VES por USD) ***
            return data['conversion_rates']['VES']
        else:
            logger.error("La respuesta de la API no contiene la tasa de VES.")
            return None 

    except requests.exceptions.RequestException as e:
        logger.error(f"Error al conectar con la API de cambio: {e}")
        return None 