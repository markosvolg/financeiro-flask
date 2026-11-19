from flask import Flask
from database import criar_tabela, criar_usuario

def create_app():

    app = Flask(__name__)
    app.secret_key = "minha_chave_secreta_123"

    # Inicializa o banco
    criar_tabela()
    criar_usuario()

    # Importa e registra os Blueprints (módulos)
    from routes.auth import auth_bp
    from routes.views import views_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    return app

if __name__ == "__main__":
    # Você precisa instanciar o app chamando a função antes de rodar
    app = create_app() 
    app.run(debug=True)


"""
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


"""

   # return jsonify({"mensagem": "Despesas Cadastrada com Sucesso"})


"""
@app.route("/")
def home():
    return render_template(
        "index.html"
    )
"""


