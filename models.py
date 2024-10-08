import psycopg2
from psycopg2 import sql

# Função para abrir a conexão com o banco de dados
def get_db_connection():
    conn = psycopg2.connect(
        host="dpg-crl0au2j1k6c738llksg-a.oregon-postgres.render.com",
        database="flask_aplicativo",
        user="flask_aplicativo_user",
        password="cDSi5A5EW0ljKrAgmda2BPydRdv3ifjF"
    )
    return conn

# Criação das tabelas (executado uma vez, fora das rotas)
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        loginUser VARCHAR(50) PRIMARY KEY,
        senha VARCHAR(100) NOT NULL,
        tipoUser VARCHAR(10) NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100),
        loginUser VARCHAR(50) REFERENCES users(loginUser),
        qtde INT,
        preco DECIMAL(10, 2)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

# Executar a função de criação de tabelas quando o app é iniciado
create_tables()
