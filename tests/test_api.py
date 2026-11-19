# tests/test_api.py

def test_home(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200

def test_receita(cliente):
    # 1. FORÇAR O LOGIN: Cria a sessão dizendo que o usuário 1 está logado
    with cliente.session_transaction() as sess:
        sess['usuario'] = 1 

    # 2. Agora sim, faz o POST para a rota CORRETA da API
    resposta = cliente.post(
        "/api/movimentacoes", # <-- AQUI ESTÁ A CORREÇÃO (rota unificada)
        json={
            "descricao": "Pagamento",
            "valor": 5000,
            "data": "2025-11-10",
            "tipo": "receita" # <-- A API exige o tipo agora
        }
    )
    
    # 3. Verifica se retornou 200 (Sucesso)
    assert resposta.status_code == 200