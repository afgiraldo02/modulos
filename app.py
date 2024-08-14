from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

# Inicialización de la aplicación Flask y configuración de la carpeta de plantillas
app = Flask(__name__, template_folder='templates')

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'  # Dirección del servidor MySQL
app.config['MYSQL_USER'] = 'root'       # Usuario de MySQL
app.config['MYSQL_PASSWORD'] = ''       # Contraseña del usuario de MySQL
app.config['MYSQL_DB'] = 'login'        # Nombre de la base de datos a la que se conectará
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Para obtener los resultados de las consultas como diccionarios
mysql = MySQL(app)  # Inicialización de la extensión MySQL con la configuración anterior

# Clave secreta para gestionar sesiones y mensajes flash
app.secret_key = 'andres'

# Ruta para la página principal
@app.route('/')
def home():
    return render_template('sitio/index.html')  # Renderiza la plantilla HTML 'index.html'

# Ruta para el manejo del login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':  # Si el método es POST, se procesa el formulario de login
        username = request.form['username']  # Obtiene el nombre de usuario del formulario
        password = request.form['password']  # Obtiene la contraseña del formulario

        # Consulta a la base de datos para verificar las credenciales del usuario
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (username, password))
        account = cur.fetchone()  # Obtiene el primer resultado de la consulta
        cur.close()

        if account:  # Si se encuentra una cuenta que coincide
            session['logged_in'] = True  # Marca al usuario como logueado
            session['id'] = account['id']  # Guarda el ID del usuario en la sesión
            session['role'] = account['id_rol']  # Guarda el rol del usuario en la sesión

            # Redirige al usuario a diferentes páginas según su rol
            if session['role'] == 1:
                return redirect(url_for('admin'))
            elif session['role'] == 2:
                return redirect(url_for('usuario'))
        else:
            # Si las credenciales no coinciden, muestra un mensaje de error
            flash("Usuario o Contraseña Incorrectas")
            return redirect(url_for('home'))

    return render_template('index.html')  # Si el método es GET, muestra la página de login

# Ruta para mostrar la página de registro
@app.route('/register')
def register():
    return render_template('sitio/registro.html')  # Renderiza la plantilla HTML 'registro.html'

# Ruta para manejar la creación de un nuevo usuario
@app.route('/crear-registro', methods=["POST"])
def crear_registro():
    correo = request.form['txtCorreo']  # Obtiene el correo del formulario de registro
    password = request.form['txtPassword']  # Obtiene la contraseña del formulario de registro

    # Inserta el nuevo usuario en la base de datos
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuarios (correo, password, id_rol) VALUES (%s, %s, '2')", (correo, password))
    mysql.connection.commit()  # Confirma la transacción
    cur.close()

    # Muestra un mensaje de éxito y redirige a la página principal
    flash("Usuario Registrado Exitosamente")
    return redirect(url_for('home'))

# Ruta para la página del administrador
@app.route('/admin')
def admin():
    return render_template('admin/index.html')  # Renderiza la plantilla HTML 'admin.html'

# Ruta para la página del usuario
@app.route('/usuario')
def usuario():
    return render_template('usuarios/usuario.html')  # Renderiza la plantilla HTML 'usuario.html'


# Nuevas rutas para API (JSON)

# Registro vía API (JSON)
@app.route('/AVANCE_DEL_PROYECTO/register', methods=['POST'])
def api_register():
    data = request.get_json()
    correo = data.get('correo')
    password = data.get('password')
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuarios (correo, password, id_rol) VALUES (%s, %s, '2')", (correo, password))
    mysql.connection.commit()
    
    return jsonify({"message": "Usuario registrado con éxito"}), 201

# Login vía API (JSON)
@app.route('/AVANCE_DEL_PROYECTO/login', methods=['POST'])
def api_login():
    data = request.get_json()
    correo = data.get('correo')
    password = data.get('password')
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (correo, password,))
    account = cur.fetchone()
    
    if account:
        session['logueado'] = True
        session['id'] = account['id']
        session['id_rol'] = account['id_rol']
        
        return jsonify({"message": "Login exitoso", "id_rol": session['id_rol']}), 200
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401

# Punto de entrada de la aplicación
if __name__ == '__main__':
    app.run(debug=True)  # Ejecuta la aplicación en modo de depuración



