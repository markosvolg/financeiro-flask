# tests/conftest.py
import sys
import os
import pytest

# Adiciona a raiz do projeto ao sys.path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app import create_app

@pytest.fixture
def app():
    """Cria a instância do app para os testes"""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def cliente(app):
    """Cria o cliente de teste que fará as requisições HTTP"""
    return app.test_client()