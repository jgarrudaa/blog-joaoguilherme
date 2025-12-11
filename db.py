import mysql.connector
from werkzeug.security import check_password_hash
from config import * # importando as variáveis do config.py


# Função para se conectar ao Banco de Dados SQL
def conectar():
    conexao = mysql.connector.connect(
        host=HOST,   # variável do config.py
        user=USER,   # variável do config.py
        password=PASSWORD,   # variável do config.py
        database=DATABASE   # variável do config.py
    )
    if conexao.is_connected():
        print("Conexão com BD OK!")
    
    return conexao

# Função para listar todas as postagens
def listar_posts():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)  
            cursor.execute("SELECT p.*, u.userName, u.picture FROM post p INNER JOIN users u ON u.idUser = p.idUser WHERE u.ativo = 1 ORDER BY idPost DESC") 
            return cursor.fetchall()
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return []
    
def listar_usuarios():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)  
            cursor.execute("SELECT * FROM users") 
            return cursor.fetchall()
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return []

def adicionar_post(title, content, idUser):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO post (title, content, idUser) VALUES (%s, %s, %s)"
            cursor.execute(sql, (title, content, idUser))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False

def adicionar_user(name, userName, passwordHash, picture):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO users (name, userName, passwordHash, picture) VALUES (%s, %s, %s, %s)"
            params = (name, userName, passwordHash, picture)
            print("DEBUG SQL:", sql, "params:", params)
            cursor.execute(sql, params)
            conexao.commit()
            return True, "ok"
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return False, erro
    
def verificar_usuario(userName, password):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT * FROM users WHERE userName = %s;"
            cursor.execute(sql, (userName,))
            usuario_encontrado = cursor.fetchone()
            if usuario_encontrado:
                if usuario_encontrado['passwordHash'] == '1234' and password == '1234':
                    return True, usuario_encontrado
                if check_password_hash(usuario_encontrado['passwordHash'], password):
                    return True, usuario_encontrado
            return False, None
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return False, None
    
def alterar_status(idUser):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT ativo FROM users WHERE idUser = %s;"
            cursor.execute(sql, (idUser,))
            status = cursor.fetchone()

            if status['ativo'] == 1: 
                sql = "UPDATE users SET ativo = 0 WHERE idUser = %s"
            else:
                sql = "UPDATE users SET ativo = 1 WHERE idUser = %s"

            cursor.execute(sql, (idUser,))
            conexao.commit()
            return True 
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False, None
    
def delete_usuario(idUser):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "DELETE FROM users WHERE idUser = %s"
            cursor.execute(sql, (idUser,))
            conexao.commit()
            return True 
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False
    
def atualizar_post(idPost, title, content):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE post SET title = %s, content = %s WHERE idPost = %s"
            cursor.execute(sql, (title, content, idPost))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False

def totais():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM vw_total_post")
            total_posts = cursor.fetchone()
            
            cursor.execute("SELECT * FROM vw_usuarios")
            total_usuarios = cursor.fetchone()

            return total_posts, total_usuarios
    
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return None, None
    
def reset_senha(idUser):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "UPDATE users SET passwordHash = '1234' WHERE idUser = %s"
            cursor.execute(sql, (idUser,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False
    
def alterar_senha(senha_hash, idUser):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "UPDATE users SET passwordHash = %s WHERE idUser = %s"
            cursor.execute(sql, (senha_hash, idUser))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False
    
def editar_perfil(name, userName, picture, idUser):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            if picture:
                sql = "UPDATE users SET name = %s, userName = %s, picture = %s WHERE idUser = %s"
                cursor.execute(sql, (name, userName, picture, idUser))
            else:
                sql = "UPDATE users SET name = %s, userName = %s WHERE idUser = %s"
                cursor.execute(sql, (name, userName, idUser))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False
        
    