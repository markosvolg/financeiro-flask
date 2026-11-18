import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "financeiro.db")


def conectar():

    print("BANCO:", DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)

    return conn

def criar_tabela():
    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes(
    id Integer primary key autoincrement,
    descricao text,
    valor real,
    tipo text,
    data_movimentacao Date
    )

    """)

    conn.commit()
    conn.close()

def criar_usuario():

    print("CRIANDO TABELA USUARIOS")
    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    email TEXT UNIQUE,
    senha TEXT
    )

    """)

    conn.commit()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """)
    print(cursor.fetchall())

    conn.close()