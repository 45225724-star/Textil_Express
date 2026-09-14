# auth_module.py
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import Usuario

# Inicializar base de datos y tablas al ejecutar
init_db()

def registrar_usuario(nombre, email, password, rol="cliente"):
    db: Session = SessionLocal()
    try:
        # Verificar si el usuario ya existe
        usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario_existente:
            print(f"Error: El correo {email} ya se encuentra registrado.")
            return False
        
        # Crear y registrar el nuevo usuario
        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password, rol=rol)
        db.add(nuevo_usuario)
        db.commit()
        print(f"¡Usuario '{nombre}' registrado exitosamente en la Base de Datos!")
        return True
    except Exception as e:
        db.rollback()
        print(f"Error al registrar usuario: {e}")
        return False
    finally:
        db.close()

def login_usuario(email, password):
    db: Session = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.password == password).first()
        if usuario:
            print(f"Login exitoso. Bienvenido, {usuario.nombre} [Rol: {usuario.rol.upper()}].")
            return usuario
        else:
            print("Error: Credenciales incorrectas o usuario no registrado.")
            return None
    finally:
        db.close()

# Bloque de prueba local ejecutando: python auth_module.py
if __name__ == "__main__":
    print("--- PRUEBA DEL MÓDULO DE LOGIN Y REGISTRO ---")
    registrar_usuario("Milton Porras", "milton@textilexpress.com", "pass123", "cliente")
    login_usuario("milton@textilexpress.com", "pass123")