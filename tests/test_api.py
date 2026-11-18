from app import app

def test_home():

    cliente = app.test_client()

    resposta = cliente.get("/")

    assert resposta.status_code == 200

def test_receita():
    cliente = app.test_client()

    resposta = cliente.post(
        "/receita",
        json={
            "descricao":"Pagamento",
            "valor":5000
        }
    )

    assert resposta.status_code == 200

