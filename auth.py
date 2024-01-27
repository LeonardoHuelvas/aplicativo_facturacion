import bcrypt
from database import create_server_connection



def hash_password(password):
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed

def verify_login(username, password):
    connection = create_server_connection("localhost", "root", "123", "lucmonet")
    cursor = connection.cursor()
    query = "SELECT password FROM usuarios WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    
    if result:
        stored_password = result[0].encode('utf-8') if isinstance(result[0], str) else result[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored_password)
    else:
        return False

def insert_user(username, password):
    connection = create_server_connection("localhost", "root", "123", "lucmonet")
    hashed_password = hash_password(password)
    cursor = connection.cursor()
    query = "INSERT INTO usuarios (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, hashed_password.decode('utf-8')))
    connection.commit()
