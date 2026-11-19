import sys
import os
import pytest

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)



from app import create_app

@pytest.fixture
def cliente():
    """Cria um cliente de teste usando a fábrica do app"""
    app = create_app()
    # Configurações extras para teste (opcional)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # Desabilita CSRF se houver
    
    with app.test_client() as cliente:
        yield cliente

def test_home():

    resposta = cliente.get("/")

    assert resposta.status_code == 200

def test_receita():
    
    resposta = cliente.post(
        "/receitas", # Corrigido de /receita para /receitas
        json={
            "descricao":"Pagamento",
            "valor":5000,
            "data":"2025-11-10"
        }
    )

    assert resposta.status_code == 200

