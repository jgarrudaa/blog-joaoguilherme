from flask import Flask, render_template, request, redirect, flash, session
from db import *
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash
from config import *

# Acessar variáveis de ambiente
secret_key = SECRET_KEY
usuario_admin = USUARIO_ADMIN
senha_admin = SENHA_ADMIN

# Informa o tipo do app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
app.secret_key = secret_key

# Rota Página Inicial
@app.route('/')
def index():
    postagens = listar_posts()
    return render_template("index.html", postagens=postagens)

# Rota do form de postagem
@app.route('/novopost', methods=['GET', 'POST'])
def novopost():
    if request.method == 'GET':
        return redirect("/")
    else:
        titulo = request.form['titulo'].strip()
        conteudo = request.form['conteudo'].strip()
        idUser = session['idUser']

        if not titulo or not conteudo:
            flash("Por favor, preencha todos os campos!")
            return redirect("/")
        
        post = adicionar_post(titulo, conteudo, idUser)
        if post:
            flash("Postagem realizada com sucesso!")
        else:
            flash("ERRO! Falha ao postar.")

        # Encaminhar para a rota da página inicial

        return redirect("/")

# Rota para editar post
@app.route('/editarpost/<int:idPost>', methods=['GET', 'POST'])
def editarpost(idPost):

    if 'user' not in session and 'admin' not in session:
        return redirect("/")
    
    # Checar a autoria do post
    with conectar() as conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(f"SELECT idUser FROM post WHERE idPost = {idPost}")
        autor = cursor.fetchone()       
        if not autor or autor['idUser'] != session['idUser']:
            print("Você não tem permissão para editar esta postagem.")
            return redirect("/")

    
    if request.method == 'GET':
        try:
            with conectar() as conexao:
                cursor = conexao.cursor(dictionary=True)  
                cursor.execute("SELECT * FROM post WHERE idPost = %s", (idPost,))
                post = cursor.fetchone()
                postagens = listar_posts()
                return render_template("index.html", postagens=postagens, post=post)
        except mysql.connector.Error as erro:
            print(f"ERRO DE BD! Erro: {erro}")
            flash("Houve um erro! Tente mais tarde!.")
            return redirect("/")
        
    # Gravar os dados alterados
    if request.method == 'POST':
        # Pegando as informações do formulário
        title = request.form['titulo'].strip()
        content = request.form['conteudo'].strip()

        if not title or not content:
            flash("Por favor, preencha todos os campos!")
            return redirect(f"/editarpost/{idPost}")
        
        sucesso = atualizar_post(idPost, title, content)

        if sucesso:
            flash("Postagem atualizada com sucesso!")
        else:
            flash("Houve um erro! Tente mais tarde!.")
        return redirect("/")
        
# Rota para excluir post
@app.route('/excluirpost/<int:idPost>')
def excluirpost(idPost):
        if not session:
            print("Usuário não autenticado tentando excluir post.")
            return redirect("/")
        
        try: 
            with conectar() as conexao:
                cursor = conexao.cursor(dictionary=True)
                if 'admin' not in session:
                    cursor.execute(f"SELECT idUser FROM post WHERE idPost = {idPost}")
                    autor_post = cursor.fetchone()

                    if not autor_post or autor_post['idUser'] != session.get('idUser'):
                        print("Tentativa de exclusão não autorizada.")
                        flash("Você não tem permissão para excluir esta postagem.")
                        return redirect("/")
                    
                cursor.execute(f"DELETE FROM post WHERE idPost = {idPost}")
                conexao.commit()
                flash("Postagem excluída com sucesso!")
                
                if 'admin' in session:
                    return redirect("/dashboard")
                else:
                    return redirect("/")
            
        except mysql.connector.Error as erro:
            conexao.rollback()
            print(f"ERRO DE BD! Erro: {erro}")
            flash("Houve um erro! Tente mais tarde!.")
            return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        username = request.form['username'].lower().strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash("Por favor, preencha todos os campos!")
            return redirect('/login')
        
        # 1° Verificar se é admin
        if username == usuario_admin and password == senha_admin:
            session['admin'] = True
            return redirect('/dashboard')
        
        # 2° Verificar se é um usuário cadastrado
        resultado, usuario_encontrado = verificar_usuario(username, password)
        if resultado:

            # Usuário banido 
            if usuario_encontrado['ativo'] == 0:
                flash("Usuário banido. Contate o suporte para mais informações.")
                return redirect('/login')
            
            # Usuário com senha resetada
            if usuario_encontrado['passwordHash'] == "1234":
                session['idUser'] = usuario_encontrado['idUser']
                return render_template('nova_senha.html')

            session['idUser'] = usuario_encontrado['idUser']
            session['user'] = usuario_encontrado['userName']
            session['foto'] = usuario_encontrado['picture']
            return redirect('/')  
        
        # 3° Usuário não encontrado
        else:
            flash("Usuário ou senha inválidos!")
            return redirect('/login')
        
# Área da(a) admin
@app.route('/dashboard')
def dashboard():
    if not session or 'admin' not in session:
        return redirect('/')
    
    posts = listar_posts()
    usuarios = listar_usuarios()
    total_posts, total_usuarios = totais()
    return render_template("dashboard.html", posts=posts, usuarios=usuarios, total_posts=total_posts, total_usuarios=total_usuarios)

# Rota para logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Rota para cadastro de usuário
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template("sign-up.html")
    elif request.method == 'POST':
        username = request.form['username'].lower().strip()
        password = request.form['password'].strip()
        name = request.form['name'].strip()
        if not name or not username or not password:
            flash("Por favor, preencha todos os campos!")
            return redirect('/sign-up')
        password_hash = generate_password_hash(password)

        picture = "placeholder.jpg" # Foto padrão de perfil
        resultado, erro = adicionar_user(name, username, password_hash, picture)

        if resultado:
            flash("Usuário cadastrado com sucesso! Faça login.")
            return redirect('/login')
        else:
            if hasattr(erro, 'errno') and erro.errno == 1062:
                flash("Nome de usuário já existe. Escolha outro.")
            else:
                flash("Erro ao cadastrar usuário. Tente novamente ou procure o suporte.")
            return redirect('/sign-up')
        
@app.route('/usuario/status/<int:idUser>')
def status_usario(idUser):
    if not session:
        return redirect('/')
    sucesso = alterar_status(idUser)
    if sucesso:
        flash("Status do usuário alterado com sucesso!")
    else:
        flash("Erro ao alterar status do usuário. Tente novamente.")
    return redirect('/dashboard')

@app.route('/usuario/excluir/<int:idUser>')
def excluir_usuario(idUser):
    if 'admin' not in session:
        return redirect('/')
    
    sucesso = delete_usuario(idUser)

    if sucesso:
        flash("Usuário excluído com sucesso!")
    else:
        flash("Erro ao excluir usuário. Tente novamente.")

    return redirect('/dashboard')

# Rota para resetar senha
@app.route('/usuario/reset/<int:idUser>')
def reset(idUser):
    if 'admin' not in session:
        return redirect('/')

    sucesso = reset_senha(idUser)
    if sucesso:
        flash("Senha resetada com sucesso!")
    else:
        flash("Erro ao resetar senha. Tente novamente.")
    return redirect('/dashboard')

# Rota para salvar a nova senha
@app.route('/usuario/novasenha', methods=['GET', 'POST'])
def novasenha():
    if 'idUser' not in session:
        return redirect('/')
    
    if request.method == 'GET':
        return render_template('nova_senha.html')
    
    if request.method == 'POST':
        senha = request.form['new_password']
        confirmacao = request.form['confirm_password'].strip()

        if not senha or not confirmacao:
            flash("Por favor, preencha todos os campos!")
            return render_template ('nova_senha.html')
        if senha != confirmacao:
            flash("As senhas não coincidem!")
            return render_template ('nova_senha.html')
        if senha == '1234':
            flash("A nova senha não pode ser '1234'. Escolha outra.")
            return render_template ('nova_senha.html')
        
        senha_hash = generate_password_hash(senha)
        idUsuario = session['idUser']
        sucesso = alterar_senha(senha_hash, idUsuario)
        if sucesso:
            flash("Senha alterada com sucesso! Faça login.")
            if 'user' in session:
                return redirect('/profile')
            
            return redirect('/login')
        else:
            flash("Erro ao alterar senha. Tente novamente.")
            return render_template ('nova_senha.html')
    
# Rota do perfil do usuário
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect('/login')
    
    if request.method == 'GET':
        listas_usuario = listar_usuarios()
        usuario = None
        for u in listas_usuario:
            if u['idUser'] == session['idUser']:
                usuario = u
                break
        return render_template("profile.html", nome=usuario['name'], user=usuario['userName'], foto=usuario['picture'])
    
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        user = request.form['user'].strip()
        foto = request.files['foto']
        idUsuario = session['idUser']
        nome_foto = ""

        if not nome or not user:
            flash('Por favor, preencha todos os campos!')
            return redirect('/profile')
        if foto:
            if foto.filename == '':
                flash('Nenhum arquivo selecionado para upload.')
                return redirect('/profile')
            extensao = foto.filename.rsplit('.', 1)[-1].lower()
            if extensao not in ('png', 'jpg', 'webp'):
                flash('Formato de arquivo inválido. Use png, jpg ou webp.')
                return redirect('/profile')
            if len(foto.read()) > 2 * 1024 * 1024:
                flash('Arquivo muito grande. O tamanho máximo é 2MB.')
                return redirect('/profile')
            
            foto.seek(0)  # Resetar o ponteiro do arquivo após a leitura
            nome_foto = f"{idUsuario}.{extensao}"

        sucesso = editar_perfil(nome, user, nome_foto, idUsuario)
        if sucesso:
            if foto:
                # salva no caminho completo configurado em app.config['UPLOAD_FOLDER']
                caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], nome_foto)
                foto.save(caminho_completo)
            flash('Perfil atualizado com sucesso!')        
        else:
            flash('Erro ao atualizar perfil. Tente novamente.')
        return redirect('/profile')

# ERRO 404
@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template("e404.html")

# ERRO 500 - ERROS INTERNOS DO SERVIDOR
@app.errorhandler(500)
def erro_interno_do_servidor(error):
    return render_template("e500.html")

# Sempre no final do arquivo
if __name__ == '__main__': 
    app.run(debug=True)

