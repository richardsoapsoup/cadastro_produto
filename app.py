from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import get_db_connection

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Página inicial
@app.route('/')
def index():
    if 'loginUser' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Rota para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loginUser = request.form['loginUser']
        senha = request.form['senha']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE loginUser = %s AND senha = %s", (loginUser, senha))
        user = cur.fetchone()
        
        cur.close()
        conn.close()  # Fecha a conexão após o uso
        
        if user:
            session['loginUser'] = loginUser
            session['tipoUser'] = user[2]
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Cadastro de usuários
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        loginUser = request.form['loginUser']
        senha = request.form['senha']
        tipoUser = request.form['tipoUser']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (loginUser, senha, tipoUser) VALUES (%s, %s, %s)", 
                    (loginUser, senha, tipoUser))
        conn.commit()
        cur.close()
        conn.close()  # Fecha a conexão após o uso
        
        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('login'))
    
    return render_template('register_user.html')

# Cadastro de produtos
@app.route('/register_product', methods=['GET', 'POST'])
def register_product():
    if 'loginUser' not in session:
        return render_template('login.html', msg='Voce precisa logar para acessar')
    
    loginUser = session['loginUser']
    tipoUser = session['tipoUser']
    
    if request.method == 'POST':
        nome = request.form['nome']
        qtde = request.form['qtde']
        preco = request.form['preco']
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar quantos produtos já foram cadastrados por este usuário
        cur.execute("SELECT COUNT(*) FROM produtos WHERE loginUser = %s", (loginUser,))
        product_count = cur.fetchone()[0]
        
        # Verificar se o usuário normal atingiu o limite de 3 produtos
        if tipoUser == 'normal' and product_count >= 3:
            flash('Usuários normais podem cadastrar no máximo 3 produtos.')
            cur.close()
            conn.close()
            return redirect(url_for('register_product'))
        

        else:
        
            # Se o limite não for atingido, o produto pode ser cadastrado
            cur.execute("INSERT INTO produtos (nome, loginUser, qtde, preco) VALUES (%s, %s, %s, %s)", 
                        (nome, loginUser, qtde, preco))
            conn.commit()

            # Mensagem de sucesso deve ser definida apenas após o cadastro bem-sucedido
            flash('Produto cadastrado com sucesso!')
            cur.close()
            conn.close()

            # Redireciona para evitar re-envio de formulário em caso de atualização da página
            return redirect(url_for('register_product'))

    return render_template('register_product.html')


@app.route('/list_products')
def list_products():
    if 'loginUser' not in session:
        return render_template('login.html', products=products, msg='Voce precisa logar para acessar')

    loginUser = session['loginUser']

    conn = get_db_connection()
    cur = conn.cursor()

    # Consultar os produtos cadastrados pelo usuário logado
    cur.execute("SELECT nome, qtde, preco FROM produtos WHERE loginUser = %s", (loginUser,))
    products = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('list_products.html', products=products)



# Logout
@app.route('/logout')
def logout():
    session.pop('loginUser', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
