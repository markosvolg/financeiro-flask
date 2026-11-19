import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from app import app

def test_login():
    cliente = app.test_client()

    resposta = cliente.post(
        "/login",
        data={
            "email":"admin@gmail.com",
            "senha":"123456"
        }
    )

    assert resposta.status_code in [200,302]