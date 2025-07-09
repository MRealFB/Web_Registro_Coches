from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# URL base de datos SQLite local
DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@app.before_request
def create_tables():
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS vehiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT NOT NULL,
                nombre TEXT NOT NULL,
                modelo TEXT NOT NULL
            )
        '''))

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        if user == 'admin' and pw == 'admin123':
            session['user'] = user
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/vehiculos')
def vehiculos():
    if 'user' not in session:
        return redirect(url_for('login'))
    search = request.args.get('search', '')
    with engine.connect() as conn:
        if search:
            query = text("""
                SELECT * FROM vehiculos
                WHERE matricula LIKE :s OR nombre LIKE :s OR modelo LIKE :s
                ORDER BY id DESC
            """)
            vehiculos = conn.execute(query, {"s": f"%{search}%"}).fetchall()
        else:
            query = text("SELECT * FROM vehiculos ORDER BY id DESC")
            vehiculos = conn.execute(query).fetchall()
    return render_template('vehiculos.html', vehiculos=vehiculos, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        matricula = request.form['matricula']
        nombre = request.form['nombre']
        modelo = request.form['modelo']
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO vehiculos (matricula, nombre, modelo) VALUES (:matricula, :nombre, :modelo)"),
                         {"matricula": matricula, "nombre": nombre, "modelo": modelo})
        return redirect(url_for('vehiculos'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    with engine.connect() as conn:
        if request.method == 'POST':
            matricula = request.form['matricula']
            nombre = request.form['nombre']
            modelo = request.form['modelo']
            conn.execute(text("""
                UPDATE vehiculos SET matricula=:matricula, nombre=:nombre, modelo=:modelo WHERE id=:id
            """), {"matricula": matricula, "nombre": nombre, "modelo": modelo, "id": id})
            return redirect(url_for('vehiculos'))
        query = text("SELECT * FROM vehiculos WHERE id=:id")
        vehiculo = conn.execute(query, {"id": id}).fetchone()
    if vehiculo is None:
        return redirect(url_for('vehiculos'))
    return render_template('edit.html', vehiculo=vehiculo)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM vehiculos WHERE id=:id"), {"id": id})
    flash('Vehículo eliminado', 'success')
    return redirect(url_for('vehiculos'))

@app.route('/export')
def export():
    if 'user' not in session:
        return redirect(url_for('login'))
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM vehiculos ORDER BY id DESC")).fetchall()
    output = "Matrícula,Nombre,Modelo\n"
    for row in rows:
        output += f"{row['matricula']},{row['nombre']},{row['modelo']}\n"
    return output, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=vehiculos.csv'
    }

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

