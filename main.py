# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, abort
import json
import os

app = Flask(__name__, static_folder='static')

# Archivo donde se almacenarán las coordenadas
DATA_FILE = 'ubicaciones.json'
# Usamos una variable de entorno para la contraseña (Seguridad)
ADMIN_PASSWORD = os.environ.get('APP_PASSWORD', 'MiClaveSegura123')

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def guardar_datos(datos):
    with open(DATA_FILE, 'w') as f:
        json.dump(datos, f)

@app.route('/')
def index():
    return render_template('invitacion.html')

@app.route('/admin/mapa')
def mapa():
    # Seguridad: Solo permite entrar si la URL tiene ?key=TU_CLAVE
    key = request.args.get('key')
    if key != ADMIN_PASSWORD:
        abort(403)
    return render_template('mapa_proyectos.html')

@app.route('/guardar_ubicacion', methods=['POST'])
def guardar_ubicacion():
    try:
        data = request.get_json()
        id_dispositivo = data.get('id_fijo', request.remote_addr)
        lat = data.get('lat')
        lon = data.get('lon')
        
        if lat and lon:
            historial = cargar_datos()
            nueva_pos = {
                "id": id_dispositivo,
                "lat": float(lat),
                "lng": float(lon)
            }
            historial.append(nueva_pos)
            
            # Mantenemos solo los últimos 50 puntos
            if len(historial) > 50:
                historial = historial[-50:]
                
            guardar_datos(historial)
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400
    except Exception as e:
        print(f"Error en servidor: {e}")
        return jsonify({"status": "error"}), 400

@app.route('/api/historial')
def api_historial():
    # Nota: Podrías añadir la misma seguridad aquí si no quieres que sea público
    return jsonify(cargar_datos())

if __name__ == '__main__':
    # En producción el puerto es gestionado por la plataforma
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)