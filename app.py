import streamlit as st
import auth
from panels import mostrar_interfaz_carga_servicios, show_panels
from database import create_server_connection, get_clientes

# Crear una variable booleana para controlar la visibilidad del formulario de inicio de sesión
mostrar_inicio_sesion = True
 

# Función para manejar el inicio de sesión
def handle_login():
    global mostrar_inicio_sesion  # Declarar como global para actualizar la variable
    login_username = st.text_input("Nombre de Usuario", key="login_username")
    login_password = st.text_input("Contraseña", type="password", key="login_password")
    login_button = st.button("Iniciar Sesión")

    if login_button:
        # Muestra un indicador de carga
        with st.spinner("Iniciando sesión..."):
            if auth.verify_login(login_username, login_password):
                st.session_state['logged_in'] = True
                mostrar_inicio_sesion = False  # Oculta el formulario de inicio de sesión
                st.success("Inicio de sesión exitoso")
            else:
                st.error("Error en el inicio de sesión")

# Función para manejar el inicio de sesión
def handle_login():
    global mostrar_inicio_sesion  # Declarar como global para actualizar la variable
    login_username = st.text_input("Nombre de Usuario", key="login_username")
    login_password = st.text_input("Contraseña", type="password", key="login_password")
    login_button = st.button("Iniciar Sesión")

    if login_button:
        # Muestra un indicador de carga
        with st.spinner("Iniciando sesión..."):
            if auth.verify_login(login_username, login_password):
                st.session_state['logged_in'] = True
                mostrar_inicio_sesion = False  # Oculta el formulario de inicio de sesión
                st.success("Inicio de sesión exitoso")
            else:
                st.error("Error en el inicio de sesión")

# Función principal
def main():
    st.title("Sistema de Facturación")
    # Crear una variable de estado para controlar si se ha iniciado sesión
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        # Mostrar el panel de inicio de sesión solo si no ha iniciado sesión
        if mostrar_inicio_sesion:
            st.subheader("Iniciar Sesión")
            handle_login()
    else:
        # Si se ha iniciado sesión, muestra el panel de opciones y obtiene la selección del panel
        selected_panel = show_panels(st)
        if selected_panel == "Opciones de Facturación":
            st.header("Opciones de Facturación")
            try:
                # Establecer conexión con la base de datos
                connection = create_server_connection("localhost", "root", "123", "lucmonet")

                # Lógica de facturación
                clientes = get_clientes(connection)
                if len(clientes) > 0:
                    cliente_id = st.selectbox("Seleccionar Cliente", clientes)
                    st.session_state['selected_cliente_id'] = cliente_id  # Almacena el cliente seleccionado en la sesión
                else:
                    st.warning("No hay clientes disponibles en este momento.")
                
                # Panel para cargar servicios
                st.subheader("Cargar Servicios")

                # Mostrar la interfaz de servicios si se ha seleccionado un cliente
                if 'selected_cliente_id' in st.session_state:
                    cliente_id = st.session_state['selected_cliente_id']
                    mostrar_interfaz_carga_servicios(cliente_id, connection)

            finally:
                # Cerrar la conexión con la base de datos
                if connection.is_connected():
                    connection.close()
                    st.write("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    main()