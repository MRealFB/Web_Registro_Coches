from flask import Flask, render_template, request, redirect, url_for, send_file, jsonift
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)
DATABASE_URL = "sqlite:///database.db"

# Crear la base si no existe
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT NOT NULL,
            nombre TEXT NOT NULL,
            modelo TEXT NOT NULL
        )
    """))

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

from flask import request

@app.route('/vehiculos')
def vehiculos():
    q = request.args.get('q', '').strip()
    with engine.connect() as conn:
        if q:
            sql = text("""
                SELECT * FROM vehiculos 
                WHERE matricula LIKE :q OR nombre LIKE :q OR modelo LIKE :q
            """)
            resultado = conn.execute(sql, {"q": f"%{q}%"})
        else:
            sql = text("SELECT * FROM vehiculos")
            resultado = conn.execute(sql)
        vehiculos = resultado.fetchall()
    return render_template('vehiculos.html', vehiculos=vehiculos)



@app.route('/add', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        matricula = request.form['matricula']
        nombre = request.form['nombre']
        modelo = request.form['modelo']
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO vehiculos (matricula, nombre, modelo)
                VALUES (:matricula, :nombre, :modelo)
            """), {"matricula": matricula, "nombre": nombre, "modelo": modelo})
        return redirect('/vehiculos')
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_vehicle(id):
    if request.method == 'POST':
        matricula = request.form['matricula']
        nombre = request.form['nombre']
        modelo = request.form['modelo']
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE vehiculos SET matricula=:matricula, nombre=:nombre, modelo=:modelo WHERE id=:id
            """), {"matricula": matricula, "nombre": nombre, "modelo": modelo, "id": id})
        return redirect('/vehiculos')
    else:
        with engine.connect() as conn:
            resultado = conn.execute(text("SELECT * FROM vehiculos WHERE id = :id"), {"id": id})
            vehiculo = resultado.fetchone()
        return render_template('edit.html', vehiculo=vehiculo)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_vehicle(id):
    if request.method == 'POST':
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM vehiculos WHERE id = :id"), {"id": id})
        return redirect('/vehiculos')
    else:
        with engine.connect() as conn:
            resultado = conn.execute(text("SELECT * FROM vehiculos WHERE id = :id"), {"id": id})
            vehiculo = resultado.fetchone()
        return render_template('confirm_delete.html', vehiculo=vehiculo)

@app.route('/exportar_db')
def exportar_db():
    return send_file('database.db', as_attachment=True)

from flask import jsonify

@app.route('/api/registrar_matricula', methods=['POST'])
def registrar_matricula():
    data = request.get_json()
    matricula = data.get('matricula')
    nombre = data.get('nombre', 'Desconocido')
    modelo = data.get('modelo', 'Desconocido')

    if not matricula:
        return jsonify({'error': 'Falta matrícula'}), 400

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO vehiculos (matricula, nombre, modelo)
            VALUES (:matricula, :nombre, :modelo)
        """), {"matricula": matricula, "nombre": nombre, "modelo": modelo})

    return jsonify({'status': 'ok', 'mensaje': 'Vehículo registrado'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
