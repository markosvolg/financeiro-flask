from flask import Blueprint, render_template
from database import conectar
from routes.auth import login_required

views_bp = Blueprint('views', __name__)


@views_bp.route("/")
def pagina_home():
    return render_template("index.html")

@views_bp.route("/dashboard")
@login_required
def pagina_dashboard():

    
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

@views_bp.route("/usuarios")
@login_required
def pagina_usuarios():

    return render_template("usuarios.html")

@views_bp.route("/receitas")
@login_required
def pagina_receitas():

    return render_template("receitas.html")

@views_bp.route("/despesas")
@login_required
def pagina_despesas():

    return render_template("despesas.html")
