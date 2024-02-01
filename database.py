import mysql.connector
from mysql.connector import Error
import traceback
import streamlit as st 


# ................................................................................................
# Función para crear la conexión a la bd
def create_server_connection(host, user, passwd, db):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=db
        )
        print("Conexión a MySQL exitosa")
    except Error as e:
        print(f"Error: '{e}'")
    return connection
# ................................................................................................
# Función para crear servicios
def insert_service(nombre, descripcion, precio, connection):
    try:
        with connection.cursor() as cursor:
            query = "INSERT INTO servicios (nombre, descripcion, precio) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, descripcion, precio))
            connection.commit()
            return True
    except Error as e:
        print(f"Error: {e}")
        return False
# ................................................................................................
# Función para crear clientes
def insert_clientes(nombre, direccion, telefono, email, fecha_registro, connection):
    try:
        cursor = connection.cursor()
        query = " INSERT INTO clientes (nombre, direccion, telefono, email, fecha_registro) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (nombre, direccion, telefono, email, fecha_registro))    
        connection.commit()
        return True
    except Error as e:
        print(f"Error'{e}'")
        return False
# ................................................................................................
# Obtener facturas
def get_facturas(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT cliente_id, factura_id FROM facturas")   
        facturas = cursor.fetchall()  # Obtiene todas las filas de la consulta
        return facturas
    except Error as e:
        error_code = e.args[0]
        error_message = e.args[1]
        print(f"Error: {error_code} - {error_message}")
        if error_code == 1064:
        # El error se debe a un error de sintaxis
            consulta = e.args[2]
            print(f"La consulta es incorrecta: {consulta}")
        else:
            # El error se debe a otra causa
            return None
# ................................................................................................   
# Se utiliza para obtener los clientes
def get_clientes(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nombre FROM clientes")
            return [{'id': row[0], 'nombre': row[1]} for row in cursor.fetchall()]
    except Error as e:
        print(f"Error al obtener clientes: {e}")
        return []
# ................................................................................................
def servicio_asignados_cliente(cliente_id, connection):
    """
    Obtiene los servicios prestados a un cliente.

    Args:
        cliente_id: El ID del cliente.
        connection: La conexión a la base de datos.

    Returns:
        Una lista de objetos que representan los servicios prestados al cliente.
    """

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT s.id, s.nombre, s.descripcion, s.precio FROM asignaciones_servicios AS a 
            INNER JOIN
                servicios AS s 
            ON
                a.servicio_id = s.id
            WHERE
                a.cliente_id = %s
            """,
            (cliente_id,),
        )
        servicios_prestados = cursor.fetchall()

        # Crear una lista de objetos para representar los servicios prestados
        servicios_prestados_obj = []
        for servicio in servicios_prestados:
            servicio_obj = {
                "id": servicio[0],
                "nombre": servicio[1],
                "descripcion": servicio[2],
                "precio": servicio[3],
            }
            servicios_prestados_obj.append(servicio_obj)

        return servicios_prestados_obj
    except Error as e:
        print(f"Error al obtener servicios prestados: {e}")

# ................................................................................................
def asignar_servicio_a_cliente(cliente_id, servicio_id, cantidad, precio, connection):
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO asignaciones_servicios (cliente_id, servicio_id, cantidad, precio, fecha_asignacion)
        VALUES (%s, %s, %s, %s, NOW())
        """
        # Aquí verificamos los servicios insertados en la tabla asignaciones servicios  son correctos.
        print(f"Insertando: cliente_id={cliente_id}, servicio_id={servicio_id}, cantidad={cantidad}, precio={precio}")  
        cursor.execute(query, (cliente_id, servicio_id, cantidad, precio))
        connection.commit()
        return True
    except Error as e:
        print(f"Error al asignar servicio a cliente: {e}")
        traceback.print_exc()  # Imprime el traceback completo para depurar
        connection.rollback()
        return False


# ................................................................................................
# Función para obtener el ID del servicio por su nombre
def obtener_id_servicio_por_nombre(nombre_servicio, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM servicios WHERE nombre = %s", (nombre_servicio,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except Error as e:
        st.error(f"Error al obtener el ID del servicio: {e}")
        return None
# ................................................................................................
def obtener_cliente_por_nombre(nombre, connection):
    try:
        cursor = connection.cursor()
        query = "SELECT id, nombre, direccion, telefono, email, fecha_registro FROM clientes WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        cliente = cursor.fetchone()
        if cliente:
            return {
                'id': cliente[0],
                'nombre': cliente[1],
                'direccion': cliente[2],
                'telefono': cliente[3],
                'email': cliente[4],
                'fecha_registro': cliente[5]
            }
        else:
            return None
    except Error as e:
        print(f"Error al obtener cliente por nombre: {e}")
        return None
# ................................................................................................
def calcular_total_factura(cliente_id, connection):
    try:
        cursor = connection.cursor()
        query = """
        SELECT SUM(precio * cantidad) AS total
        FROM asignaciones_servicios
        WHERE cliente_id = %s
        """
        cursor.execute(query, (cliente_id,))
        total = cursor.fetchone()[0]
        return total or 0
    except Error as e:
        print(f"Error al calcular total de la factura: {e}")
        return 0
# ................................................................................................
def obtener_total_factura(factura_id, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT total, factura_id FROM facturas WHERE cliente_id = %s", (factura_id,))  # Change 'id_cliente' to 'cliente_id'
        total = cursor.fetchone()[0]
        return total
    except Error as e:
        print(f"Error al obtener el total de la factura: {e}")
        return None
# ................................................................................................
def obtener_servicios_asignados(cliente_id, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT cliente_id, servicio_id, cantidad, precio FROM asignaciones_servicios  WHERE cliente_id = %s 
            """,
            (cliente_id,),
        )
        servicios_asignados = cursor.fetchall()
        return servicios_asignados
    except Error as e:
        print(f"Error al obtener servicios asignados: {e}")
        return []
#............................................................................................    
# Función para guardar la asignación de servicios en la base de datos
def guardar_asignacion_servicio(cliente_id, servicio_id, cantidad, precio, connection):
    try:
        cursor = connection.cursor()
        for servicio_id in servicio_id:
            query = """
                INSERT INTO asignaciones_servicios (cliente_id, servicio_id, cantidad, precio, fecha_asignacion)
                VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (cliente_id, servicio_id, cantidad, precio))
        
        connection.commit()
        return True
    except Error as e:
        print(f"Error al guardar asignación de servicio: {e}")
        connection.rollback()  # Importante para deshacer cambios en caso de error
        return False    

#.........................................................................................
# Función para verificar si un servicio ya está asignado a un cliente
def servicio_ya_asignado(cliente_id, servicio_id, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM asignaciones_servicios WHERE cliente_id = %s AND servicio_id = %s", (cliente_id, servicio_id))
        asignacion_existente = cursor.fetchone()
        return asignacion_existente is not None
    except Error as e:
        st.error(f"Error al verificar si el servicio ya está asignado: {e}")
        return False
#........................................................................    
def obtener_detalle_cliente_por_id(cliente_id, connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT nombre, fecha_registro FROM clientes WHERE id = %s", (cliente_id,))
            row = cursor.fetchone()
            if row:
                # Suponiendo que 'row' es una tupla con los resultados
                return {"nombre": row[0], "fecha_registro": row[1]}  # Ajusta los índices según tu consulta
            return None
    except Exception as e:
        print(f"Error al obtener detalles del cliente: {e}")
        return None

# ................................................................................................
def obtener_servicios(connection):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, descripcion, precio FROM servicios")
        servicios = cursor.fetchall()
        # print(servicios)  # Esto te mostrará lo que se está obteniendo de la base de datos
        return servicios
    except Error as e:
        print(f"Error al obtener servicios: {e}")
        return None

#--------------------------------------------------------------------------------------------------------------------------
def obtener_nombre_cliente_por_id(cliente_id, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT nombre FROM clientes WHERE id = %s", (cliente_id,))
        nombre = cursor.fetchone()
        return nombre[0] if nombre else None
    except Error as e:
        st.error(f"Error al obtener el nombre del cliente: {e}")
        return None        
 # ................................................................................................
def obtener_nombre_servicio_por_id(servicio_id, connection):
  try:
    cursor = connection.cursor()
    cursor.execute("SELECT nombre FROM servicios WHERE id = %s", (servicio_id,))
    nombre = cursor.fetchone()
    return nombre[0] if nombre else None
  except Error as e:
    print(f"Error al obtener el nombre del servicio: {e}")
    return None
# ................................................................................................
def insertar_factura(cliente_id, total, descuento, connection):
    # Obtener el siguiente número de factura
    nuevo_numero_actual_formato, nuevo_numero_actual_sin_formato = obtener_siguiente_numero_actual(connection)

    if nuevo_numero_actual_formato:
        try:
            cursor = connection.cursor()

            # Verificar si ya existe una factura con el mismo número de factura para el cliente
            if factura_ya_existe(cliente_id, nuevo_numero_actual_sin_formato, connection):
                print(f"Ya existe una factura con el número {nuevo_numero_actual_formato} para este cliente.")
                return None

            # Si no existe, insertar la nueva factura
            query = "INSERT INTO facturas (factura_id, cliente_id, total, descuento) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nuevo_numero_actual_sin_formato, cliente_id, total, descuento))
            connection.commit()

            # Actualizar la secuencia de facturas
            actualizar_secuencia_factura(nuevo_numero_actual_sin_formato, connection)
            return cursor.lastrowid
        except Error as e:
            print(f"Error al insertar factura: {e}")
            connection.rollback()
            return None
    else:
        return None


# ................................................................................................ 
def insertar_detalle_factura(factura_id, servicio_id, cantidad, precio, total, cliente_id, descuento, connection):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO detalle_factura (factura_id, servicio_id, cantidad, precio, total, cliente_id, descuento) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (factura_id, servicio_id, cantidad, precio, total, cliente_id, descuento))
        connection.commit()
    except Error as e:
        print(f"Error al insertar detalle de factura: {e}")
        connection.rollback()
#...................................................................................................
# Función para obtener el siguiente número de factura
def obtener_siguiente_numero_actual(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT numero_actual, incremento, prefijo FROM secuencia_facturas ORDER BY fecha_Actualizacion DESC LIMIT 1")
        secuencia = cursor.fetchone()
        if secuencia:
            numero_actual, incremento, prefijo = secuencia
            nuevo_numero_actual = numero_actual + incremento
        else:
            # Si no hay registro previo, inicializamos uno.
            prefijo = "LUC"  # Aquí se define el prefijo de la factura
            nuevo_numero_actual = 1
            incremento = 1  # El incremento usual es 1
            # Inserta el registro inicial en la tabla secuencia_facturas
            cursor.execute("INSERT INTO secuencia_facturas (prefijo, numero_actual, incremento, fecha_Actualizacion) VALUES (%s, %s, %s, NOW())",
                           (prefijo, nuevo_numero_actual, incremento))
            connection.commit()
        
        nuevo_numero_actual_formato = f"{prefijo}{nuevo_numero_actual:01d}"  # Formatea con ceros a la izquierda hasta 5 dígitos
        return nuevo_numero_actual_formato, nuevo_numero_actual  # Devuelve ambos para actualizar la base de datos correctamente
    except Error as e:
        print(f"Error al obtener el siguiente número de factura: {e}")
        connection.rollback()  # En caso de error, deshace la transacción
        return None, None
# ................................................................................................
# Función para actualizar la secuencia de factura
def actualizar_secuencia_factura(nuevo_numero_actual_sin_formato, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE secuencia_facturas SET numero_actual = %s, fecha_Actualizacion = NOW() WHERE id = 1", (nuevo_numero_actual_sin_formato,))  # Asegúrate de que tu tabla tenga un ID o alguna forma de identificar la fila a actualizar
        connection.commit()
    except Error as e:
        print(f"Error al actualizar secuencia de factura: {e}")
        connection.rollback()  # En caso de error, deshace la transacción
# ................................................................................................  
def factura_ya_existe(cliente_id, numero_factura, connection):
    try:
        cursor = connection.cursor()
        query = "SELECT COUNT(*) FROM facturas WHERE cliente_id = %s AND factura_id = %s"
        cursor.execute(query, (cliente_id, numero_factura))
        count = cursor.fetchone()[0]
        return count > 0  # Devuelve True si ya existe una factura con el mismo número para el cliente
    except Error as e:
        print(f"Error al verificar si la factura existe: {e}")
        return False  # En caso de error, asumimos que la factura no existe para evitar duplicados

#......................................................................
def get_facturas_por_fecha(inicio, fin, connection):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
                SELECT
                    factura_id,
                    cliente_id,
                    total,
                    descuento,
                    fecha_creacion
                FROM
                    facturas
                WHERE
                    fecha_creacion BETWEEN %s AND %s
            """,
            (inicio, fin),
        )
        facturas = cursor.fetchall()
        return facturas
    except Error as e:
        print(f"Error al obtener facturas por fecha: {e}")
        return []
    