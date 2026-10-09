from datetime import datetime
import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = (
    'clave_secreta_super_segura_textil_express_2026_key'
)

# Configuración de la base de datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(basedir, 'instance', 'textil_express.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- Modelos de Base de Datos (ORM) ---
class Producto(db.Model):
  __tablename__ = 'productos'
  id = db.Column(db.Integer, primary_key=True)
  nombre = db.Column(db.String(100), nullable=False)
  categoria = db.Column(db.String(50), nullable=False)
  stock = db.Column(db.Integer, default=0)
  precio = db.Column(db.Float, nullable=False)


class Orden(db.Model):
  __tablename__ = 'ordenes'
  id = db.Column(db.Integer, primary_key=True)
  ticket = db.Column(db.String(20), unique=True, nullable=False)
  cliente = db.Column(db.String(100), nullable=False)
  servicio = db.Column(db.String(100), nullable=False)
  estado = db.Column(db.String(50), default='1. Recepción')
  costo = db.Column(db.Float, nullable=False)
  fecha = db.Column(db.DateTime, default=datetime.utcnow)


class Usuario(db.Model):
  __tablename__ = 'usuarios'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(100), unique=True, nullable=False)
  password = db.Column(
      db.String(255), nullable=False
  )  # Almacena el hash seguro
  rol = db.Column(db.String(20), default='cliente')


# --- Rutas y Controladores ---


@app.route('/')
@app.route('/home')
def index():
  usuario_nombre = session.get('usuario_nombre')
  return render_template('index.html', usuario_nombre=usuario_nombre)


@app.route('/login', methods=['GET', 'POST'])
def login():
  """Autenticación segura validando hashes de contraseña."""
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')

    # Consulta protegida contra inyección SQL mediante SQLAlchemy ORM (parametrizada)
    usuario = Usuario.query.filter_by(email=email).first()

    # Verificación segura del hash de la contraseña
    if usuario and check_password_hash(usuario.password, password):
      session['usuario_nombre'] = usuario.email.split('@')[0]
      if usuario.rol == 'admin':
        return redirect(url_for('admin_dashboard'))
      else:
        flash('Inicio de sesión exitoso.', 'success')
        return redirect(url_for('index'))
    else:
      flash('Credenciales inválidas. Intente nuevamente.', 'danger')

  return render_template('login.html')


@app.route('/logout')
def logout():
  session.pop('usuario_nombre', None)
  flash('Sesión cerrada correctamente.', 'success')
  return redirect(url_for('index'))


@app.route('/cotizador', methods=['GET', 'POST'])
def cotizador():
  presupuesto = None
  detalle = None

  if request.method == 'POST':
    prenda = request.form.get('prenda')
    servicio = request.form.get('servicio')
    urgencia = int(request.form.get('urgencia', 1))

    precios_base = {'Pantalón': 60.0, 'Vestido': 120.0, 'Chaqueta': 95.0}
    precio_servicio = {'Entallado': 35.0, 'Dobladillo': 20.0, 'Cierre': 45.0}

    costo_calculado = precios_base.get(prenda, 0.0) + precio_servicio.get(
        servicio, 0.0
    )
    multiplicador_urgencia = 1.5 if urgencia == 2 else 1.0
    presupuesto = costo_calculado * multiplicador_urgencia
    detalle = f'{prenda} - {servicio}'

  return render_template(
      'cotizador.html', presupuesto=presupuesto, detalle=detalle
  )


@app.route('/catalogo')
def catalogo():
  productos = Producto.query.all()
  return render_template('catalogo.html', productos=productos)


@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
  orden_encontrada = None
  if request.method == 'POST':
    ticket = request.form.get('ticket')
    orden_encontrada = Orden.query.filter_by(ticket=ticket).first()
    if not orden_encontrada:
      flash('Número de ticket no encontrado.', 'warning')

  return render_template('tracking.html', orden=orden_encontrada)


@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
  if not Orden.query.first():
    db.session.add(
        Orden(
            ticket='TKT-001',
            cliente='Ana Torres',
            servicio='Entallado Vestido',
            costo=150.0,
            estado='2. En Taller',
        )
    )
    db.session.add(
        Orden(
            ticket='TKT-002',
            cliente='Carlos Ruiz',
            servicio='Cambio Cierre',
            costo=45.0,
            estado='1. Recepción',
        )
    )

    # Creación de usuarios con contraseñas cifradas (Hasheadas)
    db.session.add(
        Usuario(
            email='admin@textilexpress.com',
            password=generate_password_hash('adminpassword'),
            rol='admin',
        )
    )
    db.session.add(
        Usuario(
            email='cliente@mail.com',
            password=generate_password_hash('clientepassword'),
            rol='cliente',
        )
    )

    db.session.add(
        Producto(
            nombre='Hilo Poliéster Negro',
            categoria='Hilos',
            stock=50,
            precio=10.0,
        )
    )
    db.session.add(
        Producto(
            nombre='Cierre YKK 60cm Marrón',
            categoria='Cierres',
            stock=20,
            precio=18.0,
        )
    )
    db.session.commit()

  if request.method == 'POST':
    orden_id = request.form.get('orden_id')
    nuevo_estado = request.form.get('nuevo_estado')
    orden = Orden.query.get(orden_id)
    if orden:
      orden.estado = nuevo_estado
      db.session.commit()
      flash('Estado de la orden actualizado.', 'success')

  ordenes_activas = Orden.query.all()
  return render_template('admin.html', ordenes=ordenes_activas)


if __name__ == '__main__':
  if not os.path.exists(os.path.join(basedir, 'instance', 'textil_express.db')):
    if not os.path.exists(os.path.join(basedir, 'instance')):
      os.makedirs(os.path.join(basedir, 'instance'))
    with app.app_context():
      db.create_all()
      print('Base de datos creada exitosamente con seguridad activa.')

  app.run(debug=True, port=5000)