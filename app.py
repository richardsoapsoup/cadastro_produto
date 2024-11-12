from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import get_db_connection
import custoso as cus
import pandas as pd
import plotly.express as px
import plotly.io as pio
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ASKDL244LFD'




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
        comando = cur.execute("SELECT * FROM users WHERE loginUser = %s AND senha = %s", (loginUser, senha))
        cus.exemploThread(comando)
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

# Rota para vender um produto
@app.route('/sell_product/<nome>', methods=['POST'])
def sell_product(nome):
    if 'loginUser' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Reduz a quantidade em 1 do produto, se a quantidade for maior que 0
    cur.execute("UPDATE produtos SET qtde = qtde - 1 WHERE loginUser = %s AND nome = %s AND qtde > 0", 
                (session['loginUser'], nome))
    
    # Registrar a venda na tabela 'vendas'
    cur.execute("""
        INSERT INTO vendas (nome_produto, loginUser, tipo_transacao, quantidade)
        VALUES (%s, %s, %s, %s)
    """, (nome, session['loginUser'], 'venda', 1))

    conn.commit()
    cur.close()
    conn.close()

    flash(f'Você vendeu uma unidade de {nome}.')
    return redirect(url_for('list_products'))




@app.route('/buy_product/<nome>', methods=['POST'])
def buy_product(nome):
    if 'loginUser' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Atualiza a quantidade de produtos no inventário
    cur.execute("UPDATE produtos SET qtde = qtde + 1 WHERE loginUser = %s AND nome = %s", 
                (session['loginUser'], nome))
    
    # Define a data da compra para hoje
    data_compra = datetime.now().date()
    
    # Verifica se já existe uma entrada para o produto na data de hoje
    cur.execute("""
    SELECT quantidade FROM vendas 
    WHERE nome_produto = %s AND loginUser  = %s AND tipo_transacao = %s AND data = %s
    """, (nome, session['loginUser'], 'compra', data_compra))
    
    resultado = cur.fetchone()

    if resultado:
        # Atualiza a quantidade na transação existente
        nova_quantidade = resultado[0] + 1
        cur.execute("""
            UPDATE vendas 
            SET quantidade = %s 
            WHERE nome_produto = %s AND loginUser  = %s AND tipo_transacao = %s AND data = %s
        """, (nova_quantidade, nome, session['loginUser'], 'compra', data_compra))
    else:
        # Insere uma nova entrada com a quantidade inicial de 1
        cur.execute("""
            INSERT INTO vendas (nome_produto, loginUser, tipo_transacao, quantidade, data)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, session['loginUser'], 'compra', 1, data_compra))

    conn.commit()
    cur.close()
    conn.close()

    flash(f'Você comprou uma unidade de {nome}.')
    return redirect(url_for('list_products'))

    
        
    


@app.route('/transacoes')
def visualizar_transacoes():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Seleciona todas as vendas agrupadas por data e nome do produto
    cur.execute("SELECT nome_produto, data, SUM(quantidade) AS quantidade FROM vendas GROUP BY nome_produto, data")
    vendas = cur.fetchall()
    
    # Converte os dados para um DataFrame do Pandas
    df = pd.DataFrame(vendas, columns=['nome_produto', 'data', 'quantidade'])
    print(df)  # Verifique se os dados estão corretos
    
    # Cria o gráfico de barras
    fig = px.bar(
        df,
        x='data',
        y='quantidade',
        color='nome_produto',
        title='Vendas de Produtos ao Longo do Tempo',
        labels={'data': 'Data', 'quantidade': 'Quantidade de Vendas'}
    )
    
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Data",
        yaxis_title="Quantidade de Vendas"
    )
    
    # Converte o gráfico para HTML para exibir na página
    graph_html = fig.to_html(full_html=False)
    
    return render_template('transacoes.html', graph_html=graph_html)





    
   

if __name__ == '__main__':
    app.run(debug=True)
    
