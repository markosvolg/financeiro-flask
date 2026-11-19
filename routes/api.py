from flask import Blueprint, jsonify, request
from database import conectar
from routes.auth import login_required
from werkzeug.security import generate_password_hash

api_bp = Blueprint('api', __name__)

# ==========================================
# API DE USUÁRIOS
# ==========================================
@api_bp.route("/api/usuarios")
@login_required
def api_usuarios():
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, email FROM usuarios")
        dados = cursor.fetchall()
        usuarios = [{"id": r[0], "usuario": r[1], "email": r[2]} for r in dados]
        return jsonify(usuarios)
    finally:
        conn.close()

@api_bp.route("/api/usuarios/<int:id>", methods=["PUT"])
@login_required
def api_atualizar_usuario(id):
    dados = request.json
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET usuario = ?, email = ? WHERE id = ?", 
                       (dados["usuario"], dados["email"], id))
        
        if dados.get("senha"):
            senha_hash = generate_password_hash(dados["senha"])
            cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, id))
            
        conn.commit()
        return jsonify({"mensagem": "Usuário atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        conn.close()

@api_bp.route("/api/usuarios/<int:id>", methods=["DELETE"])
@login_required
def api_deletar_usuario(id):
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        conn.commit()
        return jsonify({"mensagem": "Usuário excluído com sucesso!"})
    finally:
        conn.close()

# ==========================================
# API DE MOVIMENTAÇÕES (Receitas e Despesas)
# ==========================================
@api_bp.route("/api/movimentacoes")
@login_required
def api_listar_movimentacoes():
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, descricao, valor, tipo, data_movimentacao FROM movimentacoes")
        dados = [{"id": r[0], "descricao": r[1], "valor": r[2], "tipo": r[3], "data": r[4]} for r in cursor.fetchall()] 
    finally:  
        conn.close()
    return jsonify(dados)

@api_bp.route("/api/movimentacoes", methods=["POST"])
@login_required
def api_criar_movimentacao():
    dados = request.json
    if not dados.get("data") or not dados.get("tipo"):
        return jsonify({"erro": "Dados incompletos"}), 400
        
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO movimentacoes (descricao, valor, tipo, data_movimentacao)
            VALUES (?, ?, ?, ?)
        """, (dados["descricao"], dados["valor"], dados["tipo"], dados["data"]))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"mensagem": "Cadastro realizado com sucesso!"})

@api_bp.route("/api/movimentacoes/<int:id>", methods=["PUT"])
@login_required
def api_atualizar_movimentacao(id):
    dados = request.json
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE movimentacoes 
            SET descricao = ?, valor = ?, data_movimentacao = ? 
            WHERE id = ?
        """, (dados["descricao"], dados["valor"], dados["data"], id))
        conn.commit()
        return jsonify({"mensagem": "Atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        conn.close()

@api_bp.route("/api/movimentacoes/<int:id>", methods=["DELETE"])
@login_required
def api_deletar_movimentacao(id):
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movimentacoes WHERE id = ?", (id,))
        conn.commit()
        return jsonify({"mensagem": "Excluído com sucesso!"})
    finally:
        conn.close()

# ==========================================
# API DE GRÁFICOS
# ==========================================
@api_bp.route("/api/resumo")
@login_required
def api_resumo():
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT tipo, SUM(valor) FROM movimentacoes GROUP BY tipo")
        dados = cursor.fetchall()
        return jsonify(dados)
    finally:
        conn.close()

@api_bp.route("/api/evolucao")
@login_required
def api_evolucao():
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%m', data_movimentacao) as mes, tipo, SUM(valor)
            FROM movimentacoes
            GROUP BY strftime('%m', data_movimentacao), tipo
            ORDER BY mes
        """)
        dados = cursor.fetchall()
        return jsonify(dados)
    finally:
        conn.close()