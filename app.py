from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.dialects.postgresql import JSON
from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2 
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '12345678'

DB_HOST = "ec2-54-80-123-146.compute-1.amazonaws.com"
DB_NAME = "df77lhet7i10re"
DB_USER = "qsfqfambtgynhx"
DB_PASS = "04170f56eac3e66bc92566c4e2d4a76312092033d0cb10ac45ce7992579477e2"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


@app.route('/')
def home():
    # Verifique se o usuário está logado
    if 'loggedin' in session:
    
        # O usuário está logado mostre a página inicial
        return render_template('home.html', username=session['username'])
    # O usuário não está logado redirecionar para a página de login
    return redirect(url_for('login'))
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Verifique se existem solicitações POST de "nome de usuário" e "senha" (formulário enviado pelo usuário)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Verifique se a conta existe usando o Postgree
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Buscar um registro e retornar o resultado
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            print(password_rs)
            # Se a conta existir na tabela de usuários no banco de dados
            if check_password_hash(password_rs, password):
                # Criar dados de sessão, podemos acessar esses dados em outras rotas
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirecionar para a página inicial
                return redirect(url_for('home'))
            else:
                # Conta não existe ou nome de usuário/senha incorretos
                flash('Incorrect username/password')
        else:
            # Conta não existe ou nome de usuário/senha incorretos
            flash('Incorrect username/password')
 
    return render_template('login.html')
  
@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Verifique se existem solicitações POST "username", "password" e "email" (formulário enviado pelo usuário)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Crie variáveis ​​para facilitar o acesso
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Verifique se a conta existe usando Postgree
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # Se a conta existir, mostre as verificações de erro e validação
        if account:
            flash('A conta já existe!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Endereço de e-mail inválido!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('O nome de usuário deve conter apenas caracteres e números!')
        elif not username or not password or not email:
            flash('Por favor, preencha o formulário!')
        else:
            # A conta não existe e os dados do formulário são válidos, agora insira uma nova conta na tabela de usuários
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('Você se registrou com sucesso!')
    elif request.method == 'POST':
        # O formulário está vazio... (sem dados POST)
        flash('Por favor, preencha o formulário!')
        flash('Please fill out the form!')
    # Mostrar formulário de inscrição com mensagem (se houver)
    return render_template('register.html')
   
   
@app.route('/logout')
def logout():
    # Remova os dados da sessão, isso desconectará o usuário
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirecionar para a página de login
   return redirect(url_for('login'))
  
@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Verifique se o usuário está logado
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Mostrar a página de perfil com informações da conta
        return render_template('profile.html', account=account)
    # O usuário não está logado redirecionar para a página de login
    return redirect(url_for('login'))
 
if __name__ == "__main__":
    app.run(debug=True)

