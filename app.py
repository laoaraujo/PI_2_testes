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
        departamento = request.form['departamento']
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
            cursor.execute("INSERT INTO users (departamento, username, password, email) VALUES (%s,%s,%s,%s)", (departamento, username, _hashed_password, email))
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




@app.route('/tabelaoption')
def tabelaoption(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Verifique se o usuário está logado
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()


        # Mostrar a página de perfil com informações da conta
        return render_template('tabelaoption.html', account=account)

    # O usuário não está logado redirecionar para a página de login
    return redirect(url_for('login'))


@app.route('/index')
def index(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Verifique se o usuário está logado
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        s = "SELECT * FROM students"
        cur.execute(s) # Execute the SQL
        list_users = cur.fetchall()
        # Mostrar a página de perfil com informações da conta
        return render_template('index.html', account=account, list_users = list_users)
    # O usuário não está logado redirecionar para a página de login
    return redirect(url_for('login'))




@app.route('/tabela')
def tabela(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Verifique se o usuário está logado
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()


        # Mostrar a página de perfil com informações da conta
        return render_template('tabela.html', account=account)

    # O usuário não está logado redirecionar para a página de login
    return redirect(url_for('login'))



@app.route('/add_student', methods=['POST'])
def add_student():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        livre= request.form['livre']
        usuario = request.form['usuario']
        departamento= request.form['departamento']
        nomel= request.form['nomel']
        nomeresponsavel = request.form['nomeresponsavel']
        parentesco = request.form['parentesco']
        descricao= request.form['descricao']
        cur.execute("INSERT INTO students (livre, usuario, departamento, nomel, nomeresponsavel,parentesco,descricao) VALUES (%s,%s,%s,%s,%s,%s,%s)", (livre, usuario, departamento,nomel, nomeresponsavel,parentesco,descricao ))
        conn.commit()
        flash('Registrado com Sucesso')
        return redirect(url_for('tabela'))
 
@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_employee(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM students WHERE id = %s', [id])
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit.html', student = data[0])

 
@app.route('/update/<id>', methods=['POST'])
def update_student(id):
    if request.method == 'POST':
        livre= request.form['livre']
        usuario = request.form['usuario']
        departamento = request.form['departamento']
        nomel= request.form['nomel']
        nomeresponsavel = request.form['nomeresponsavel']
        parentesco = request.form['parentesco']
        descricao= request.form['descricao']
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE students
            SET livre = %s,
                usuario = %s,
                departamento = %s,
                nomel = %s,
                nomeresponsavel= %s,
                parentesco = %s,
                descricao= %s
            WHERE id = %s
        """, (livre, usuario, departamento, nomel, nomeresponsavel,parentesco, descricao , id))
        flash('Registro Atualizado com sucesso')
        conn.commit()
        return redirect(url_for('index'))

@app.route('/edit2/<id>', methods = ['POST', 'GET'])
def get_employee2(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('SELECT * FROM students WHERE id = %s', [id])
    data = cur.fetchall()
    cur.close()
    print(data[0])
    return render_template('edit2.html', student = data[0])

 
@app.route('/update2/<id>', methods=['POST'])
def update_student2(id):
    if request.method == 'POST':
    
        parentesco = request.form['parentesco']
        
         
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            UPDATE students
            SET 
                parentesco = %s
            
            WHERE id = %s
        """, (parentesco, id))
        flash('Registro Atualizado com sucesso')
        conn.commit()
        return redirect(url_for('index'))
 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_student(id):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    cur.execute('DELETE FROM students WHERE id = {0}'.format(id))
    conn.commit()
    flash('Registro deletado com Sucesso')
    return redirect(url_for('index'))
 
if __name__ == "__main__":
    app.run(debug=True)


