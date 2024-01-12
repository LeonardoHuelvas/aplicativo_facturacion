import mysql.connector
from mysql.connector import Error
 

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

# Obtener facturas
def get_facturas(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id_cliente FROM facturas")   
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
        
# Se utiliza para obtener los clientes
def get_clientes(connection):
  try:
    cursor = connection.cursor()
    cursor.execute("SELECT nombre FROM clientes")
    clientes = cursor.fetchall()
    return [str(tupla[0]) for tupla in clientes]
  except Error as e:
    print(f"Error al obtener clientes: {e}")
    return None

def get_servicios_prestados(cliente_id, connection):
    """
    Obtiene los servicios prestados a un cliente.

    Args:
        cliente_id: El ID del cliente.
        connection: La conexión a la base de datos.

    Returns:
        Una lista de objetos `FacturaDetalle` que representan los servicios prestados al cliente.
    """

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                servicio_id,
                cantidad,
                precio,
                total
            FROM
                servicios_clientes
            WHERE
                cliente_id = %s
            """,
            (cliente_id,),
        )
        servicios_prestados = cursor.fetchall()
        return [get_facturas(servicio_id, cantidad, precio, total) for servicio_id, cantidad, precio, total in servicios_prestados]
    except Error as e:
        print(f"Error al obtener servicios prestados: {e}")
        return None
