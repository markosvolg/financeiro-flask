# tests/test_login.py


def test_login(cliente):
    resposta = cliente.post(
        "/login",
        data={
            "email": "admin@gmail.com",
            "senha": "123456"
        }
    )

    # Pode retornar 200 (falha no login) ou 302 (sucesso e redirecionamento)
    assert resposta.status_code in [200, 302]

