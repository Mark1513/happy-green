import pytest

from happy_green.services import ServicoFinanceiro
from tests.fakes import RepositorioEmMemoria


@pytest.fixture
def service():
    return ServicoFinanceiro(RepositorioEmMemoria())
