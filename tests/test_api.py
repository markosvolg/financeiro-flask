# tests/test_api.py

def test_home(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200

def test_receita(cliente):
    # 1. FORÇAR O LOGIN: Cria a sessão dizendo que o usuário 1 está logado
    with cliente.session_transaction() as sess:
        sess['usuario'] = 1 # Coloque um ID de usuário válido aqui

    # 2. Agora sim, faz o POST da receita
    resposta = cliente.post(
        "/receitas",
        json={
            "descricao": "Pagamento",
            "valor": 5000,
            "data": "2025-11-10"
        }
    )
    
    # Agora ele deve retornar 200 com a mensagem de sucesso!
    assert resposta.status_code == 200