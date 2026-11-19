from flask import Flask, redirect, session
from flask import request
from flask import jsonify
from database import *
from flask import render_template
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from functools import wraps

from database import DB_PATH

app = Flask(__name__)

app.secret_key = "minha_chave_secreta_123"

criar_tabela()
criar_usuario()




@app.route("/cadastro", methods=["GET", "POST"])
def cadastro_usuario():
    if request.method =="POST":

        usuario = request.form["usuario"].strip()
        email = request.form["email"].strip()
        senha = request.form["senha"].strip()


        senha_hash = generate_password_hash(senha)
     
        conn = conectar()
    
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO usuarios
        (
            usuario,
            email,
            senha
        )
        VALUES (?,?,?)
        """,
        (
            usuario,
            email,
            senha_hash
        ))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("cadastro.html")
    


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method =="POST":

        email = request.form["email"].strip()    
        senha = request.form["senha"].strip()   

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute("select * from usuarios where email = ?", (email,))

        usuario = cursor.fetchone()



        if usuario:
            print(
                check_password_hash(
                usuario[3],
                senha
                )
            )    

      #  print("EMAIL DIGITADO:", email)
      #  print("RESULTADO:", usuario)

        conn.close()

        if usuario and check_password_hash ( usuario[3], senha):
            print("LOGIN OK")

            session["usuario"] = usuario[0]

            return redirect("/dashboard")
        
    return render_template("login.html")

def login_required(f):
    @wraps(f) 
    def decorated(*args, **kwargs):

        if "usuario"not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated

@app.route("/api/usuarios")
@login_required
def usuarios():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        usuario,
        email
    FROM usuarios
    """)

    dados = cursor.fetchall()

    conn.close()

    return jsonify(dados)

@app.route("/dashboard")
@login_required
def dashboard():

    print("SESSAO:", session)
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT tipo,
           SUM(valor)
    FROM movimentacoes
    GROUP BY tipo
    """)

    resumo = cursor.fetchall()

    conn.close()

    return render_template("/dashboard.html", resumo = resumo)

@app.route("/api/resumo")
@login_required
def resumo():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("select tipo, sum(valor) from movimentacoes group by tipo")

    dados = cursor.fetchall()

    conn.close()

    return jsonify(dados)


@app.route("/api/evolucao")
@login_required
def evolucao():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        strftime('%m', data_movimentacao) as mes,
        tipo,
        SUM(valor)
    FROM movimentacoes
    GROUP BY
        strftime('%m', data_movimentacao),
        tipo
    ORDER BY mes
    """)

    dados = cursor.fetchall()

    conn.close()

    return jsonify(dados)


def inserir_movimentacao(descricao, valor, tipo,data):
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO movimentacoes (descricao, valor, tipo,data_movimentacao) VALUES (?, ?, ?,?)",
            (descricao, valor, tipo,data)
        )
        conn.commit()          # ✅ com parênteses
    finally:
        conn.close()


@app.route("/receita", methods=["POST"]) # Routa de receita
def receita():

    dados = request.json

    data_movimentacao = dados.get("data")

    if not data_movimentacao:
        return jsonify({
        "erro": "data_movimentacao obrigatória"
        }), 400

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movimentacoes(descricao, valor, tipo, data_movimentacao)
        VALUES (?,?,?,?)

    """,
    (dados["descricao"],
         dados["valor"],
         "receita",
         data_movimentacao
         ))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Receita Cadastrada com Sucesso"})    


@app.route("/despesa", methods=["POST"])   
def despesa():
    dados = request.get_json(silent=True) or {}
    if not dados.get("descricao") or dados.get("valor") is None:
        return jsonify({"erro": "descricao e valor são obrigatórios"}), 400
    
        
    conn = conectar()
    try:
         cursor = conn.cursor()

         cursor.execute("""
            INSERT INTO movimentacoes(descricao, valor, tipo,data_movimentacao) VALUES (?,?,?,?)""", (dados["descricao"], dados["valor"],"despesa",dados["data"] )
            )
         conn.commit()
    finally:
         conn.close()

    return jsonify({"mensagem": "Despesas Cadastrada com Sucesso"})

@app.route("/movimentacoes")

def lista():

    conn = conectar()
    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT descricao, valor, tipo FROM movimentacoes
        """)

        dados = [
            {"descricao": r[0], "valor":r[1], "tipo":r[2]}
            for r in cursor.fetchall()
           ] 
    finally:  

        conn.close()

    return jsonify(dados)

@app.route("/")
def home():
    return render_template(
        "index.html"
    )

if __name__ == "__main__":
    app.run(debug=True)
