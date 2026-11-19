# tests/test_api.py

def test_home(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200

def test_receita(cliente):
    resposta = cliente.post(
        "/receitas", # Lembre-se que no app.py a rota é /receitas com 's'
        json={
            "descricao": "Pagamento",
            "valor": 5000,
            "data": "2025-11-10"
        }
    )
    assert resposta.status_code == 200
