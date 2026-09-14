# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import SessionLocal, init_db
from models import Usuario

app = Flask(__name__)
app.secret_key = "clave_secreta_textil_express" # Necesario para gestionar sesiones

# Inicializar base de datos al arrancar el servidor
init_db()

@app.route("/")
def raiz():
    # Lo primero que muestra el sistema al abrir el link es el login
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["email"]
        clave = request.form["password"]

        db = SessionLocal()
        try:
            # Buscar el usuario en la base de datos SQLite
            usuario = db.query(Usuario).filter(Usuario.email == correo, Usuario.password == clave).first()
            if usuario:
                # Guardar datos en la sesión del navegador
                session["usuario_nombre"] = usuario.nombre
                session["usuario_email"] = usuario.email
                flash("¡Login exitoso!", "success")
                return redirect(url_for('home'))
            else:
                flash("Correo o contraseña incorrectos.", "error")
        finally:
            db.close()

    return render_template("login.html")

@app.route("/home")
def home():
    # Validar si el usuario ha iniciado sesión previamente
    if "usuario_nombre" not in session:
        flash("Por favor, inicia sesión para acceder a la home.", "error")
        return redirect(url_for('login'))
    
    return render_template("index.html", usuario=session["usuario_nombre"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # Registrar un usuario por defecto si la BD está vacía para pruebas rápidas
    db = SessionLocal()
    if not db.query(Usuario).filter(Usuario.email == "admin@textil.com").first():
        admin_default = Usuario(nombre="Administrador Taller", email="admin@textil.com", password="123", rol="administrador")
        db.add(admin_default)
        db.commit()
    db.close()

    # Correr el servidor web local
    app.run(debug=True)