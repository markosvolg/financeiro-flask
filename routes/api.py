import io
import pandas as pd

from flask import Blueprint, jsonify, request
from database import conectar
from routes.auth import login_required
from werkzeug.security import generate_password_hash

from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
# EXPORTAÇÃO EXCEL E PDF
# ==========================================
@api_bp.route("/api/export/excel")
@login_required
def export_excel():
    conn = conectar()
    try:
        # Busca os dados do banco
        df = pd.read_sql_query("SELECT id, descricao, valor, tipo, data_movimentacao FROM movimentacoes ORDER BY data_movimentacao DESC", conn)
    finally:
        conn.close()

    # Renomeia as colunas para ficar bonito no Excel
    df.columns = ['ID', 'Descrição', 'Valor (R$)', 'Tipo', 'Data']

    # Cria um arquivo na memória (não salva no disco do servidor)
    output = io.BytesIO()
    
    # Escreve o Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Movimentações')
        
        # Ajusta a largura das colunas
        worksheet = writer.sheets['Movimentações']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + i)].width = column_len

    output.seek(0)

    # Retorna o arquivo para download
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='relatorio_financeiro.xlsx'
    )


@api_bp.route("/api/export/pdf")
@login_required
def export_pdf():
    conn = conectar()
    try:
        cursor = conn.cursor()
        
        # 1. Pegar Totais
        cursor.execute("SELECT tipo, SUM(valor) FROM movimentacoes GROUP BY tipo")
        totais = dict(cursor.fetchall()) # Retorna algo como {'receita': 15000, 'despesa': 400}
        total_receita = totais.get('receita', 0)
        total_despesa = totais.get('despesa', 0)
        saldo = total_receita - total_despesa

        # 2. Pegar Movimentações
        cursor.execute("SELECT descricao, valor, tipo, data_movimentacao FROM movimentacoes ORDER BY data_movimentacao DESC")
        movimentacoes = cursor.fetchall()
    finally:
        conn.close()

    # Cria o PDF na memória
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Centralizado

    # Título
    elements.append(Paragraph("Relatório Financeiro", title_style))
    elements.append(Spacer(1, 20))

    # Resumo (Cards no PDF)
    resumo_data = [
        ['RESUMO', 'VALOR'],
        ['Total de Receitas', f"R$ {total_receita:,.2f}"],
        ['Total de Despesas', f"R$ {total_despesa:,.2f}"],
        ['Saldo Atual', f"R$ {saldo:,.2f}"]
    ]
    
    tabela_resumo = Table(resumo_data, colWidths=[200, 150])
    tabela_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3b82f6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f3f4f6")),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(tabela_resumo)
    elements.append(Spacer(1, 30))

    # Tabela de Movimentações
    dados_tabela = [['Data', 'Descrição', 'Tipo', 'Valor']]
    
    for mov in movimentacoes:
        tipo_formatado = mov[2].capitalize()
        dados_tabela.append([mov[3], mov[0], tipo_formatado, f"R$ {mov[1]:,.2f}"])

    tabela_mov = Table(dados_tabela, colWidths=[80, 250, 80, 100])
    
    # Estilo da tabela de movimentações
    estilo_tabela = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#198754")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]
    
    # Colorir linhas de acordo com o tipo (Receita = Verde claro, Despesa = Vermelho claro)
    for i, mov in enumerate(movimentacoes, start=1):
        if mov[2] == 'receita':
            estilo_tabela.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#d1e7dd")))
        else:
            estilo_tabela.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f8d7da")))

    tabela_mov.setStyle(TableStyle(estilo_tabela))
    elements.append(tabela_mov)

    # Gera o PDF
    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='relatorio_financeiro.pdf'
    )



# ==========================================
# EXPORTAÇÃO EXCEL (USUÁRIOS)
# ==========================================
@api_bp.route("/api/export/excel_usuarios")
@login_required
def export_excel_usuarios():
    conn = conectar()
    try:
        # Verifique se os nomes das colunas estão corretos no seu banco
        df = pd.read_sql_query("SELECT id, usuario, email FROM usuarios", conn)
    finally:
        conn.close()

    df.columns = ['ID', 'Nome de Usuário', 'E-mail']

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Usuários')
        worksheet = writer.sheets['Usuários']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + i)].width = column_len

    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='lista_usuarios.xlsx')
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