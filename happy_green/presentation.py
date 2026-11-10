"""Conversão de entrada e formatação; não realiza acesso ao banco."""

import re
from decimal import Decimal

from .domain import dinheiro
from .errors import ValidationError


def ler_brl(valor: str) -> Decimal:
    valor = valor.strip().replace("R$", "").strip()
    # Aceita 1500,00 / 1.500,00 / 1500.00 / 1500. Não adivinha agrupamentos inválidos.
    if "," in valor:
        if not re.fullmatch(r"-?(?:\d+|\d{1,3}(?:\.\d{3})+),\d{1,2}", valor):
            raise ValidationError("Use um valor como 1500,00 ou 1.500,00.")
        valor = valor.replace(".", "").replace(",", ".")
    elif not re.fullmatch(r"-?\d+(?:\.\d{1,2})?", valor):
        raise ValidationError("Use um valor como 1500,00. Digite centavos com até duas casas.")
    return dinheiro(valor)


def brl(valor: Decimal) -> str:
    numero = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {numero}"
