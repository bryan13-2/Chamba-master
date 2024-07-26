from flask import Flask, render_template, request, redirect, url_for, json
from flask_mysqldb import MySQL
from config import Config
import datetime
import requests

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# Función para validar formato de fecha
def validar_fecha(fecha_str):
    try:
        datetime.datetime.strptime(fecha_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validar_formulario(tipo_busqueda, form_data):
    if tipo_busqueda == 'apellidos_nombres':
        primer_apellido = form_data.get('primer_apellido', '').strip()
        segundo_apellido = form_data.get('segundo_apellido', '').strip()
        primer_nombre = form_data.get('primer_nombre', '').strip()
        segundo_nombre = form_data.get('segundo_nombre', '').strip()
        sexo = form_data.get('sexo', '').strip()
        fecha_nacimiento = form_data.get('fecha_nacimiento', '').strip()

        if not primer_apellido or not segundo_apellido or not primer_nombre or not segundo_nombre or not sexo or not fecha_nacimiento:
            return False

        if not validar_fecha(fecha_nacimiento):
            return False

    elif tipo_busqueda == 'numero_identificacion':
        numero_identificacion = form_data.get('numero_identificacion', '').strip()
        if not numero_identificacion:
            return False

    elif tipo_busqueda == 'serial':
        serial_registro_civil = form_data.get('serial_registro_civil', '').strip()
        if not serial_registro_civil:
            return False

    elif tipo_busqueda == 'todos_criterios':
        numero_identificacion = form_data.get('numero_identificacion', '').strip()
        primer_apellido = form_data.get('primer_apellido', '').strip()
        segundo_apellido = form_data.get('segundo_apellido', '').strip()
        primer_nombre = form_data.get('primer_nombre', '').strip()
        segundo_nombre = form_data.get('segundo_nombre', '').strip()
        sexo = form_data.get('sexo', '').strip()
        fecha_nacimiento = form_data.get('fecha_nacimiento', '').strip()

        if not numero_identificacion or not primer_apellido or not segundo_apellido or not primer_nombre or not segundo_nombre or not sexo or not fecha_nacimiento:
            return False

        if not validar_fecha(fecha_nacimiento):
            return False

    return True

# Función del reCAPTCHA
def is_human(captcha_response):
    """Validar la respuesta del reCAPTCHA desde el servidor de Google
    Retorna True si el test de reCAPTCHA fue pasado, sino retorna False.
    """
    secret = "6Ldk5BYqAAAAAH_7BM6y17MEUWFZ0cYCINUvSkoV"
    payload = {'response': captcha_response, 'secret': secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']

@app.route('/index', methods=['GET', 'POST'])
def index():
    sitekey = "6Ldk5BYqAAAAAJ7qtuqrrDk5nIRQi_7EZdc2buk7"

    if request.method == 'POST':
        tipo_registro_civil = request.form.get('tipo_registro_civil', '')
        tipo_busqueda = request.form.get('tipo_busqueda', '')

        # Validar el formulario según el tipo de búsqueda
        if not validar_formulario(tipo_busqueda, request.form):
            return render_template('error.html', message="El formulario contiene datos incorrectos.")

        # Construir las condiciones y valores para la consulta SQL
        conditions = []
        values = []

        if tipo_busqueda == 'apellidos_nombres':
            primer_apellido = request.form.get('primer_apellido', '')
            segundo_apellido = request.form.get('segundo_apellido', '')
            primer_nombre = request.form.get('primer_nombre', '')
            segundo_nombre = request.form.get('segundo_nombre', '')
            sexo = request.form.get('sexo', '')
            fecha_nacimiento = request.form.get('fecha_nacimiento', '')

            if primer_apellido:
                conditions.append("primer_apellido = %s")
                values.append(primer_apellido)

            if segundo_apellido:
                conditions.append("segundo_apellido = %s")
                values.append(segundo_apellido)

            if primer_nombre:
                conditions.append("primer_nombre = %s")
                values.append(primer_nombre)

            if segundo_nombre:
                conditions.append("segundo_nombre = %s")
                values.append(segundo_nombre)
            
            if sexo:
                conditions.append("sexo = %s")
                values.append(sexo)

            if fecha_nacimiento:
                try:
                    fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                    conditions.append("fecha_nacimiento = %s")
                    values.append(fecha_nacimiento)
                except ValueError:
                    return render_template('error.html', message="El formato de la fecha es incorrecto. Use YYYY-MM-DD.")

        elif tipo_busqueda == 'numero_identificacion':
            numero_identificacion = request.form.get('numero_identificacion', '')

            if numero_identificacion:
                conditions.append("numero_identificacion = %s")
                values.append(numero_identificacion)

        elif tipo_busqueda == 'serial':
            serial_registro_civil = request.form.get('serial_registro_civil', '')

            if serial_registro_civil:
                conditions.append("serial_registro_civil = %s")
                values.append(serial_registro_civil)

        elif tipo_busqueda == 'todos_criterios':
            numero_identificacion = request.form.get('numero_identificacion', '')
            primer_apellido = request.form.get('primer_apellido', '')
            segundo_apellido = request.form.get('segundo_apellido', '')
            primer_nombre = request.form.get('primer_nombre', '')
            segundo_nombre = request.form.get('segundo_nombre', '')
            sexo = request.form.get('sexo', '')
            fecha_nacimiento = request.form.get('fecha_nacimiento', '')

            if numero_identificacion:
                conditions.append("numero_identificacion = %s")
                values.append(numero_identificacion)

            if primer_apellido:
                conditions.append("primer_apellido = %s")
                values.append(primer_apellido)

            if segundo_apellido:
                conditions.append("segundo_apellido = %s")
                values.append(segundo_apellido)

            if primer_nombre:
                conditions.append("primer_nombre = %s")
                values.append(primer_nombre)

            if segundo_nombre:
                conditions.append("segundo_nombre = %s")
                values.append(segundo_nombre)

            if sexo:
                conditions.append("sexo = %s")
                values.append(sexo)

            if fecha_nacimiento:
                try:
                    fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                    conditions.append("fecha_nacimiento = %s")
                    values.append(fecha_nacimiento)
                except ValueError:
                    return render_template('error.html', message="El formato de la fecha es incorrecto. Use YYYY-MM-DD.")

        # Construir la consulta SQL final (seleccionando todas las columnas necesarias)
        sql = "SELECT * FROM certificados"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        cursor = mysql.connection.cursor()
        cursor.execute(sql, tuple(values))
        resultados = cursor.fetchall()
        cursor.close()

        if resultados:
            # Redirigir a la ruta /consulta con los resultados como parámetro
            return redirect(url_for('consulta', tipo_busqueda=tipo_busqueda, resultados=resultados))
        else:
            # Si no hay resultados, mostrar mensaje de error
            return render_template('error.html', message="No se encontraron registros en la base de datos.")

    # Renderizar el formulario inicial si es GET o no hay resultados
    return render_template('index.html', sitekey=sitekey)

@app.route('/')
def principal():
    return render_template('principal.html')

@app.route('/consulta')
def consulta():
    # Obtener los parámetros de la consulta desde la URL
    tipo_busqueda = request.args.get('tipo_busqueda', '')
    resultados = request.args.get('resultados')  # Asegúrate de que resultados sea una lista de tuplas

    # Asegurarse de que resultados sea una lista de tuplas
    if resultados:
        resultados = eval(resultados)  # Convertir de cadena a lista de tuplas
        if not isinstance(resultados, list):
            resultados = [resultados]  # Si es solo un resultado, convertirlo en lista

    # Renderizar la plantilla de información de consulta
    return render_template('informacion_consulta.html', tipo_busqueda=tipo_busqueda, resultados=resultados)

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'])
