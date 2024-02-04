import filecmp
import os
import pandas as pd
import streamlit as st 
import re
import datetime
from streamlit import config
from database import *
from descargar_facturas import interfaz_descargar_facturas
from factura_pdf import generar_factura_final, mostrar_factura_pdf, mostrar_previsualizacion
from styles import load_styles
from mysql.connector import Error
from decimal import Decimal

 
# ................................................................................................
# Verifica si 'servicios_añadidos' ya existe en st.session_state, si no, inicialízalo como una lista vacía
if 'servicios_añadidos' not in st.session_state:
    st.session_state.servicios_añadidos = []

st.markdown(load_styles(), unsafe_allow_html=True)
# ................................................................................................
def show_panels(st):
    st.sidebar.title("Opciones del Panel")
    panel_option = st.sidebar.radio(
        "Ir a",
        ["Crear Cliente", "Crear Servicios", "Interfaz de Servicios", "Gestionar Asignación de Servicios", "Descargar Facturas"]
    )
    
    if panel_option == "Crear Cliente":
        show_client_panel(st)
    elif panel_option == "Crear Servicios":
        show_service_panel(st)
    elif panel_option == "Interfaz de Servicios":
        connection = create_server_connection("localhost", "root", "123", "lucmonet")
        mostrar_interfaz_servicios(st, connection)
    elif panel_option == "Gestionar Asignación de Servicios":
        connection = create_server_connection("localhost", "root", "123", "lucmonet")
        mostrar_interfaz_asignacion_servicios(st, connection)
    elif panel_option == "Descargar Facturas":
        show_descargar_facturas(st)

# ................................................................................................
# Función para mostrar la interfaz de descarga de facturas
 

def show_descargar_facturas(st):
    connection = create_server_connection("localhost", "root", "123", "lucmonet")
    interfaz_descargar_facturas(get_facturas_por_fecha, obtener_detalle_cliente_por_id, obtener_cliente_por_nombre, obtener_total_factura, connection)

# ................................................................................................
def show_client_panel(st):
    st.subheader("Crear Cliente")
    with st.form(key='client_form'):
        nombre = st.text_input("Nombre")
        direccion = st.text_input("Dirección")
        telefono = st.text_input("Teléfono")
        email = st.text_input("Email")
        fecha_registro = st.date_input("Fecha de Registro")
        submit_button = st.form_submit_button(label='Crear Cliente')
        
        if submit_button:
            # Primero validamos los datos antes de intentar insertarlos
            try:
                # Validación de los campos
                validar_nombre(nombre)    
                validar_direccion(direccion)    
                validar_telefono(telefono)    
                validar_email(email)
                
                # Si todo está correcto, abrimos la conexión e intentamos insertar el cliente
                connection = create_server_connection("localhost", "root", "123", "lucmonet")
                try:
                    if insert_clientes(nombre, direccion, telefono, email, fecha_registro, connection):
                        st.success("Cliente creado con éxito")
                    else:
                        st.error("Hubo un error al crear el cliente")
                finally:
                    # Cerramos la conexión una vez finalizado el proceso
                    if connection.is_connected():
                        connection.close()
            except ValueError as e:
                # Si hay un error en la validación, mostramos el mensaje
                st.error(str(e))
           
# ................................................................................................
# Función para editar un cliente
def validar_nombre(nombre):
    if not nombre:
        raise ValueError("El nombre no puede estar vacío.")
    if not isinstance(nombre, str):
        raise ValueError("El nombre debe ser una cadena de caracteres.")
    if len(nombre) < 3:
        raise ValueError("El nombre debe tener al menos 3 caracteres.")

# ................................................................................................
def validar_direccion(direccion):
    if not direccion:
        raise ValueError("La dirección no puede estar vacía.")
    if not isinstance(direccion, str):
        raise ValueError("La dirección debe ser una cadena de caracteres.")
    if len(direccion) < 10:
        raise ValueError("La dirección debe tener al menos 10 caracteres.")
# ................................................................................................
def validar_telefono(telefono):
    """
    Valida que el número de teléfono sea válido.

    Args:
        telefono (str): El número de teléfono a validar.

    Raises:
        ValueError: Si el teléfono está vacío, no tiene 9 dígitos o no está compuesto solo por números.
    """
    if not telefono:
        raise ValueError("El teléfono no puede estar vacío.")
    if not all(char.isdigit() for char in telefono):
        raise ValueError("El teléfono debe estar compuesto solo por números, no se permiten letras ni otros caracteres.")
    if len(telefono) != 10:
        raise ValueError("El teléfono debe tener 9 dígitos.")
# ................................................................................................
def validar_email(email):
    if not isinstance(email, str):
        raise ValueError("El email debe ser una cadena de caracteres.")
    if len(email) < 10:
        raise ValueError("El email debe tener al menos 10 caracteres.")
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$", email):
        raise ValueError("El email no es válido.")

# ................................................................................................
def editar_cliente(cliente_id, nombre, direccion, telefono, email):
    # Validar los datos
    validar_nombre(nombre)
    validar_direccion(direccion)
    validar_telefono(telefono)
    validar_email(email)

    # Actualizar los datos del cliente en la base de datos
    connection = create_server_connection("localhost", "root", "123", "lucmonet")
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre = %s, direccion = %s, telefono = %s, email = %s WHERE id = %s",
        (nombre, direccion, telefono, email, cliente_id),
    )
    connection.commit()

# ................................................................................................
nombre = st.text_input("Nombre del Servicio", max_chars=50)
descripcion = st.text_area("Descripción", max_chars=255)
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
# ................................................................................................
def mostrar_interfaz_clientes(connection):
    # Obtener la lista de clientes
    clientes = get_clientes(connection)

    # Validar los datos introducidos por el usuario
    nombre = st.text_input("Nombre")
    validar_nombre(nombre)
    direccion = st.text_input("Dirección")
    validar_direccion(direccion)
    telefono = st.text_input("Teléfono")
    validar_telefono(telefono)
    email = st.text_input("Email")
    validar_email(email)

    # Mostrar la lista de clientes
    if clientes:
        st.subheader("Lista de Clientes:")
        df_clientes = pd.DataFrame(clientes, columns=["ID", "Nombre", "Dirección", "Teléfono", "Email"])
        st.dataframe(df_clientes)
# ................................................................................................
# Interfaz para servicios
def mostrar_interfaz_servicios(st,connection):
    # Obtener la lista de servicios
    servicios = obtener_servicios(connection)

    # Input para el nombre del servicio
    nombre_servicio = st.text_input( "Nombre del servicio ")
    # Validar el nombre del servicio solo si se proporciona un nombre no vacío
    if nombre_servicio.strip():  # Verifica si el nombre no está vacío después de eliminar espacios en blanco
        try:
            validar_nombre(nombre_servicio)
        except ValueError as e:
            st.error(f"Error: {str(e)}")  # Muestra un mensaje de error si la validación falla
    servicios = obtener_servicios(connection)
    if servicios:
        # Verifica que los datos no sean None o estén vacíos
        df_servicios = pd.DataFrame(servicios)
        st.dataframe(df_servicios)
    else:
        st.error("No se pudo obtener la lista de servicios.")

#----------------------------------------------------------------------------------
def mostrar_lista_servicios(servicios):
    if servicios:
        # Si servicios es una lista de diccionarios, se accede a los valores por clave, no por índice.
        for servicio in servicios:
            st.write(f"ID: {servicio['id']}, Nombre: {servicio['nombre']}, Descripción: {servicio['descripcion']}, Precio: {servicio['precio']}")
    else:
        st.write("No se encontraron servicios.")

#------------------------------------------------------------
def mostrar_interfaz_carga_servicios(st, cliente_id, connection):
    st.subheader("Cargar Servicios")
    # Obtener la lista de servicios disponibles
    servicios = obtener_servicios(connection)
    if servicios:
        # Crear una lista desplegable para que el usuario seleccione el servicio
        selected_service_name = st.selectbox("Seleccionar Servicio", [servicio['nombre'] for servicio in servicios])
        # Encontrar el servicio seleccionado en la lista de servicios para obtener el ID y el precio
        selected_service = next((servicio for servicio in servicios if servicio['nombre'] == selected_service_name), None)
        if selected_service:
            # Mostrar la cantidad y el precio del servicio seleccionado
            cantidad = st.number_input("Cantidad de servicios", min_value=1, value=1)
            precio = selected_service['precio']  # Obtener el precio desde el servicio seleccionado

            st.text("Precio por servicio: ${precio:,.2f}", style=config["style"]["text"])

            # Botón para agregar el servicio seleccionado
            if st.button("Agregar servicio"):
                # Guardar la asignación de servicio en la base de datos
                if guardar_asignacion_servicio(cliente_id, selected_service['id'], cantidad, precio, connection):
                    st.success(f"Servicio '{selected_service_name}' asignado correctamente al cliente.")
                else:
                    st.error("Hubo un error al asignar el servicio.")
            else:
                st.warning("Por favor, seleccione un servicio.")
        else:
            st.warning("No hay servicios disponibles en este momento.")

#-----------------------------------------------------------
# Función para añadir un servicio y asignarlo a un cliente
def añadir_servicio(nombre, cantidad, precio, cliente_id, connection):
    # Agrega el servicio al estado de la sesión
    servicio = {
        "nombre": nombre, 
        "cantidad": cantidad, 
        "precio": precio
    }
    
    st.session_state.servicios_añadidos.append(servicio)
    # Obtiene el ID del servicio por su nombre
    servicio_id = obtener_id_servicio_por_nombre(nombre, connection)
    if servicio_id:
        # Verifica si el servicio ya está asignado al cliente en la base de datos
        if servicio_ya_asignado(cliente_id, servicio_id, connection):
            st.error(f"El servicio '{nombre}' ya está asignado al cliente: {obtener_nombre_cliente_por_id(cliente_id, connection)}")
        else:
            # Asigna el servicio al cliente en la base de datos
            asignar_servicio_a_cliente(cliente_id, servicio_id, cantidad, precio, connection)
            st.success(f"Servicio '{nombre}' asignado correctamente al cliente: {obtener_nombre_cliente_por_id(cliente_id, connection)}")
    else:
        st.error(f"No se encontró un servicio con el nombre: {nombre}")

 
#-----------------------nuevas funciones------------------------
# Interfaz de usuario para añadir servicios
def limpiar_interfaz():
    st.session_state['servicios_añadidos'] = []
def interfaz_añadir_servicios(cliente_id, connection):
    st.subheader("Añadir Servicios al Cliente")
    servicios_disponibles = obtener_servicios(connection)
    servicios_asignados = obtener_servicios_asignados(cliente_id, connection)  # Esta función debería obtener los nombres de los servicios asignados

    if servicios_disponibles:
        selected_service_name = st.selectbox("Seleccionar Servicio", [servicio['nombre'] for servicio in servicios_disponibles])
        selected_service = next((servicio for servicio in servicios_disponibles if servicio['nombre'] == selected_service_name), None)

        if selected_service:
            cantidad_servicio = st.number_input("Cantidad", min_value=1, value=1)
            precio_servicio = selected_service['precio']
            st.text(f"Precio por servicio: {precio_servicio}")

            if st.button("Agregar servicio"):
                servicio_id = selected_service['id']

                # Multiplicamos la cantidad por el precio
                total = cantidad_servicio * precio_servicio

                if servicio_ya_asignado(cliente_id, servicio_id, connection):
                    st.warning(f"El servicio '{selected_service_name}' ya está asignado al cliente: {obtener_nombre_cliente_por_id(cliente_id, connection)}")
                else:
                    if asignar_servicio_a_cliente(cliente_id, servicio_id, cantidad_servicio, total, connection):
                        st.success(f"Servicio '{selected_service_name}' asignado correctamente al cliente.")
                    else:
                        st.error("Error al asignar el servicio.")
            else:
                st.warning("Por favor, seleccione un servicio.")
        else:
            st.warning("Por favor, seleccione un servicio.")
    else:
        st.warning("No hay servicios disponibles en este momento.")


#--------------------------------------------------------------------------------
# Asegúrate de importar correctamente las funciones necesarias desde factura_pdf.py
def mostrar_interfaz_asignacion_servicios(st, connection):
    st.subheader("Gestionar Asignación de Servicios")
    clientes = get_clientes(connection)
    
    if not clientes:
        st.error("No hay clientes disponibles, por favor, registra cliente antes de continuar")
        return 
    # Añade un elemento vacío al principio
    nombres_clientes = [""] + [cliente['nombre'] for cliente in clientes]  
    nombre_cliente_seleccionado = st.selectbox("Seleccionar Cliente", nombres_clientes)
    
    if nombre_cliente_seleccionado == "":
        st.write("Seleccione un Cliente para asignar servicios.")
        return
    
    # Asumo que obtener_id_servicio_por_nombre es una función o condición que no está definida en tu fragmento de código
    # Si es una función, debes reemplazar esta línea con la llamada correspondiente a esa función
    if nombre_cliente_seleccionado:  
        cliente_id = next((cliente['id'] for cliente in clientes if cliente['nombre'] == nombre_cliente_seleccionado), None)

        if cliente_id:
            interfaz_añadir_servicios(cliente_id, connection)
            servicios_asignados = obtener_servicios_asignados(cliente_id, connection)
            if not servicios_asignados:
                st.error("Este cliente no tiene servicios asignados. Por favor, asigna servicios antes de continuar ")
                return

            total = calcular_total_factura(cliente_id, connection)
            descuento = st.number_input("Descuento aplicado (%)", min_value=0.0, max_value=100.0, value=0.0)

            if st.button("Previsualizar Factura"):
                st.session_state['previsualizacion_datos'] = {
                    'cliente_id': cliente_id,
                    'nombre_cliente': obtener_nombre_cliente_por_id(cliente_id, connection),
                    'servicios_asignados': servicios_asignados,
                    'total': total,
                    'descuento': descuento,
                    'fecha_factura': datetime.datetime.now().strftime("%Y-%m-%d")
                }
                mostrar_previsualizacion(connection)  # Asegúrate de que esta función está definida en factura_pdf.py

            if st.button("Confirmar y Generar Factura"):
                if 'previsualizacion_datos' in st.session_state:
                    generar_factura_final()  # Asegúrate de que esta función está definida en factura_pdf.py
                else:
                    st.error("Datos de previsualización no están disponibles.")
        else:
            st.error("No hay servicios asignados para generar la factura.")
    else:
        st.error("No se seleccionó un cliente válido.")


    #  "Ver Facturas" 
    if st.button("Ver Facturas"):
        facturas = get_facturas(connection)
        if facturas:
            st.subheader("Lista de Facturas")
            for factura in facturas:
                cliente_id = factura[0]
                cliente_info = obtener_nombre_cliente_por_id(cliente_id, connection)
                st.write(f"ID: {factura[0]} - Cliente: {cliente_info} - Total: {obtener_total_factura(factura[0], connection)}")
        else:
            st.write("No hay facturas disponibles.")

#---------------------------------------------------------------------
 
if __name__ == "__main__":
    st.set_page_config(page_title="Asignación de Servicios", layout="wide")
    show_panels()