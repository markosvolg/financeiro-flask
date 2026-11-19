from flask import Blueprint, jsonify, request
from database import conectar
from routes.auth import login_required

api_bp = Blueprint('api', __name__)


@api_bp.route("/api/usuarios")
@login_required
def api_usuarios():

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

@api_bp.route("/api/resumo")
@login_required
def api_resumo():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("select tipo, sum(valor) from movimentacoes group by tipo")

    dados = cursor.fetchall()

    conn.close()

    return jsonify(dados)

@api_bp.route("/api/evolucao")
@login_required
def api_evolucao():
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

@api_bp.route("/receitas", methods=["POST"]) # Routa de receita
@login_required
def api_criar_receita():

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

 

   

@api_bp.route("/despesa", methods=["POST"])  
@login_required 
def api_criar_despesa():
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

    return jsonify({"mensagem": "Despesa Cadastrada com Sucesso"})


@api_bp.route("/movimentacoes")

def api_lista_movimentacoes():

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