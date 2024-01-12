import pandas as pd
import streamlit as st
from mysql.connector import Error
from database import (
    insert_service,
    create_server_connection,
    insert_clientes,
    get_clientes,
    get_facturas,
    
)

def show_panels(st):
    st.sidebar.title("Opciones del Panel")
    panel_option = st.sidebar.radio("Ir a", ["Crear Cliente", "Crear Servicios", "Interfaz de Servicios"])

    if panel_option == "Crear Cliente":
        show_client_panel(st)
    elif panel_option == "Crear Servicios":
        show_service_panel(st)
    elif panel_option == "Interfaz de Servicios":
        connection = create_server_connection("localhost", "root", "123", "lucmonet")  # Crea la conexión
        
        # Obtener el cliente seleccionado
        clientes = get_clientes(connection)
        cliente_id = st.selectbox("Seleccionar Cliente", clientes)

        mostrar_interfaz_servicios(connection)
    elif panel_option == "Cargar Servicios":
        connection = create_server_connection("localhost", "root", "123", "lucmonet")
        
        # Asegúrate de que cliente_id esté definido antes de llamar a la función
        if "cliente_id" in locals():
            mostrar_interfaz_carga_servicios(st, cliente_id, connection)  # Llama a la función para cargar servicios a clientes


def show_client_panel(st):
    st.subheader("Crear Cliente")
    with st.form(key='client_form'):
        nombre  = st.text_input("Nombre")
        direccion  = st.text_input("Dirección")
        telefono  = st.text_input("Teléfono")
        email  = st.text_input("Email")
        fecha_registro = st.date_input("Fecha de Registro")
        submit_button = st.form_submit_button(label='Crear Cliente')
        
        if submit_button:
            connection = create_server_connection("localhost", "root", "123", "lucmonet")
            if insert_clientes(nombre, direccion, telefono, email, fecha_registro, connection):
                st.success("Cliente creado con éxito")
            else:
                st.error("Hubo un error al crear el cliente")

def show_service_panel(st):
    st.subheader("Crear Servicios")
    with st.form(key='service_form'):
        nombre = st.text_input("Nombre del Servicio")
        descripcion = st.text_area("Descripción")
        precio = st.number_input("Precio", min_value=0.0, format='%f')
        submit_button = st.form_submit_button(label='Crear Servicio')
        
        if submit_button:
            connection = create_server_connection("localhost", "root", "123", "lucmonet")
            if insert_service(nombre, descripcion, precio, connection):
                st.success("Servicio creado con éxito")
            else:
                st.error("Hubo un error al crear el servicio.")

def mostrar_interfaz_servicios(connection):
    st.header("Interfaz de Servicios")

    # Obtener la lista de servicios desde la base de datos
    servicios = obtener_servicios(connection)

    if servicios:
        st.subheader("Lista de Servicios:")
        df_servicios = pd.DataFrame(servicios, columns=["ID", "Nombre", "Descripción", "Precio"])
        st.dataframe(df_servicios)
    else:
        st.info("No hay servicios disponibles en este momento.")

def obtener_servicios(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, nombre, descripcion, precio FROM servicios")
        servicios = cursor.fetchall()
        return servicios
    except Error as e:
        print(f"Error al obtener servicios: {e}")
        return None

def agregar_servicio_a_factura(factura_id, servicio_id, cantidad, connection):
    
    try:
        cursor = connection.cursor()
        # Obtener el precio unitario del servicio
        cursor.execute("SELECT precio FROM servicios WHERE id = %s", (servicio_id,))
        precio = cursor.fetchone()[0]
        # Calcular el total para este servicio
        total = cantidad * precio
        # Insertar el servicio en la tabla de detalles de factura
        query = """
            INSERT INTO detalles_factura (id_factura, servicio_id, cantidad, precio, total)
            VALUES (%s, %s, %s, %s, %s)
        """
        if not agregar_servicio_a_factura(factura_id, servicio_id, cantidad, connection):
          st.error("Error al agregar el servicio. El error fue: {}".format(e))
        cursor.execute(query, (factura_id, servicio_id, cantidad, precio, total))
        connection.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False

def mostrar_interfaz_carga_servicios(st, cliente_id, connection):
    # Listar los servicios disponibles
    servicios = obtener_servicios(connection)
    selected_service_ids = []  # Lista para almacenar los IDs de servicios seleccionados

    # Crear una lista de casillas de verificación para que el usuario seleccione los servicios
    selected_services = st.multiselect("Seleccionar Servicios", [servicio['nombre'] for servicio in servicios])

    # Obtener los IDs de servicios correspondientes a los nombres seleccionados
    for servicio in servicios:
        if servicio['nombre'] in selected_services:
            selected_service_ids.append(servicio['id'])

    # Solicitar la cantidad de servicios
    cantidad = st.number_input("Cantidad de servicios", min_value=1)

    # Agregar el servicio a la factura
    if st.button("Agregar servicio"):
        if agregar_servicio_a_factura(cliente_id, selected_service_ids, cantidad, connection):
            st.success("Servicio agregado correctamente")
        else:
            st.error("Error al agregar el servicio")

# Función para asignar servicios a un cliente en la base de datos
def asignar_servicios_a_cliente(cliente_id, selected_service_ids, connection):
    try:
        cursor = connection.cursor()

        # Realizar la asignación en la base de datos (por ejemplo, insertar registros en una tabla de asignaciones)
        for servicio_id in selected_service_ids:
            query = """
                INSERT INTO asignaciones_servicios (cliente_id, servicio_id)
                VALUES (%s, %s)
            """
            cursor.execute(query, (cliente_id, servicio_id))

        connection.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False


def mostrar_interfaz_facturacion(st, factura_id, connection):
    # Obtener la información de la factura
    factura = get_facturas(factura_id, connection)
    if factura:
        # Mostrar la información de la factura
        st.subheader("Factura")
        st.write("Número de factura: {}".format(factura.numero_factura))
        st.write("Fecha: {}".format(factura.fecha))
        st.write("Cliente: {}".format(factura.cliente.nombre))

        # Mostrar la lista de servicios prestados
        servicios_prestados = get_facturas.objects.filter(factura_id=factura.id)
        if servicios_prestados:
            st.subheader("Servicios prestados")
            df_servicios_prestados = pd.DataFrame(servicios_prestados, columns=["ID", "Nombre", "Descripción", "Cantidad", "Precio", "Total"])
            st.dataframe(df_servicios_prestados)

        # Mostrar el importe total
        importe_total = factura.importe_total
        st.subheader("Importe total")
        st.write("{} €".format(importe_total))

        # Botón para generar la factura en formato PDF
        st.button("Generar factura")

    else:
        st.warning("No se encuentra la factura con el ID especificado.")

if __name__ == "__main__":  
    st.title("Sistema de Facturación")
    show_panels(st)
