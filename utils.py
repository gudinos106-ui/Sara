import requests
import os

def enviar_telegram(mensaje):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ ERROR: No se encontró el Token o el Chat ID en el archivo .env")
        return False

    # --- LÓGICA INTELIGENTE DE PROXY ---
    # Solo activamos el proxy si detectamos que estamos en PythonAnywhere
    es_pythonanywhere = "PYTHONANYWHERE_DOMAIN" in os.environ
    
    proxies = None
    if es_pythonanywhere:
        proxies = {
            'http': 'http://proxy.server:3128',
            'https': 'http://proxy.server:3128',
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    
    try:
        # Si proxies es None (en tu PC), requests irá directo a internet
        response = requests.post(url, json=payload, proxies=proxies, timeout=10)
        if not response.ok:
            print(f"❌ Error de Telegram: {response.text}")
        return response.ok
    except Exception as e:
        print(f"❌ Error crítico de conexión: {e}")
        return False

# 3. FUNCIÓN DE LIMPIEZA
def limpiar_monto(texto):
    if not texto: 
        return 0.0
    
    # Convertimos a string y limpiamos símbolos
    texto = str(texto).replace('₡', '').replace(' ', '').strip()
    
    # Manejo de formatos decimales (BCR)
    if ',' in texto and '.' in texto:
        texto = texto.replace('.', '').replace(',', '.')
    elif ',' in texto:
        texto = texto.replace(',', '.')
    
    try:
        return abs(float(texto))
    except:
        return 0.0

# 4. FUNCIÓN DE CATEGORÍAS
def categorizar(concepto):
    c = str(concepto).upper()
    if any(k in c for k in ['MAXI PALI', 'MAXIPALI', 'SUPER', 'WALMART', 'AMPM', 'VINDI']): 
        return '🛒 Súper/Comida'
    if any(k in c for k in ['HELADERIA', 'RESTAURANTE', 'POLLO', 'SODA', 'CAFE', 'UBER EATS', 'SPOON']): 
        return '🍦 Gustitos/Salidas'
    if any(k in c for k in ['GASOLINERA', 'UBER', 'PEAJE', 'RITEVE', 'DEKRA']): 
        return '🚗 Transporte'
    return '❓ Otros'
