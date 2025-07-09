from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, Response, abort
from supabase import create_client, Client
import os

app = Flask(__name__)

# Configura aquí tus datos de Supabase:
SUPABASE_URL = "https://gapfbzmccgkoatleopgv.supabase.co"       # Pon tu URL Supabase
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdhcGZiem1jY2drb2F0bGVvcGd2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIwNzY2NzgsImV4cCI6MjA2NzY1MjY3OH0.fu-r_oHiGadA3f4WCO0UtOF3M59Kc1ZagtWB9SaJ7Bc"                # Pon tu API KEY Supabase

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

USUARIO = "admin"
CONTRASEÑA = "admin123"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['contraseña'] == CONTRASEÑA:
            return redirect(url_for('menu'))
        else:
            error = 'Credenciales incorrectas.'
    return render_template('login.html', error=error)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/vehiculos')
def vehiculos():
    q = request.args.get('q', '').strip()
    query = supabase.table('vehiculos').select('*')
    if q:
        query = query.or_(
            f"matricula.ilike.%{q}%,nombre.ilike.%{q}%,modelo.ilike.%{q}%"
        )
    result = query.execute()
    vehiculos = result.data
    return render_template('vehiculos.html', vehiculos=vehiculos)

@app.route('/add', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        matricula = request.form['matricula']
        nombre = request.form['nombre']
        modelo = request.form['modelo']
        supabase.table('vehiculos').insert({
            "matricula": matricula,
            "nombre": nombre,
            "modelo": modelo
        }).execute()
        return redirect('/vehiculos')
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_vehicle(id):
    if request.method == 'POST':
        matricula = request.form['matricula']
        nombre = request.form['nombre']
        modelo = request.form['modelo']
        supabase.table('vehiculos').update({
            "matricula": matricula,
            "nombre": nombre,
            "modelo": modelo
        }).eq('id', id).execute()
        return redirect('/vehiculos')
    else:
        result = supabase.table('vehiculos').select('*').eq('id', id).single().execute()
        vehiculo = result.data
        return render_template('edit.html', vehiculo=vehiculo)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_vehicle(id):
    if request.method == 'POST':
        supabase.table('vehiculos').delete().eq('id', id).execute()
        return redirect('/vehiculos')
    else:
        result = supabase.table('vehiculos').select('*').eq('id', id).single().execute()
        vehiculo = result.data
        return render_template('confirm_delete.html', vehiculo=vehiculo)

import csv
from io import StringIO
from flask import Response

@app.route('/exportar_db')
def exportar_db():
    # Traemos todos los vehículos de Supabase
    result = supabase.table('vehiculos').select('*').execute()
    vehiculos = result.data

    # Creamos un CSV en memoria
    si = StringIO()
    cw = csv.writer(si)
    # Cabecera del CSV
    cw.writerow(['ID', 'Matrícula', 'Nombre', 'Modelo'])
    # Filas con los datos
    for v in vehiculos:
        cw.writerow([v['id'], v['matricula'], v['nombre'], v['modelo']])

    output = si.getvalue()
    si.close()

    # Devolvemos el CSV como respuesta con el tipo y nombre para descarga
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=vehiculos.csv'}
    )


@app.route('/api/registrar_matricula', methods=['POST'])
def registrar_matricula():
    data = request.get_json()
    matricula = data.get('matricula')
    nombre = data.get('nombre', 'Desconocido')
    modelo = data.get('modelo', 'Desconocido')

    if not matricula:
        return jsonify({'error': 'Falta matrícula'}), 400

    supabase.table('vehiculos').insert({
        "matricula": matricula,
        "nombre": nombre,
        "modelo": modelo
    }).execute()

    return jsonify({'status': 'ok', 'mensaje': 'Vehículo registrado'}), 200

from io import BytesIO
from openpyxl import Workbook
from flask import send_file

@app.route('/exportar_excel')
def exportar_excel():
    result = supabase.table('vehiculos').select('*').execute()
    vehiculos = result.data

    wb = Workbook()
    ws = wb.active
    ws.title = "Vehículos"

    # Cabecera
    ws.append(['ID', 'Matrícula', 'Nombre', 'Modelo'])

    # Filas
    for v in vehiculos:
        ws.append([v['id'], v['matricula'], v['nombre'], v['modelo']])

    # Guardamos el archivo en memoria
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output,
                     as_attachment=True,
                     download_name="vehiculos.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')



API_KEY = "TuTokenSuperSecreto123"  # Cambia por algo seguro

@app.route('/download_backup')
def download_backup():
    token = request.args.get('token')
    if token != API_KEY:
        abort(403)  # Prohibido si no coincide el token
    # No hay archivo backup local, tendrías que implementar exportación o backup externo
    return "Backup no disponible. Implementa exportación en Supabase."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
