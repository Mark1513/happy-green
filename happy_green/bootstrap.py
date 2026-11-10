"""Composição das dependências da aplicação."""

import os

import streamlit as st

from .errors import ConfigurationError
from .repository import DatabaseConfig, RepositorioPostgres
from .services import ServicoFinanceiro


def get_service() -> ServicoFinanceiro:
    try:
        config = dict(st.secrets.get("database", {}))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        config = {}
    campos = {name: os.getenv(f"HAPPY_GREEN_DB_{name.upper()}", config.get(name))
              for name in ("host", "port", "dbname", "user", "password")}
    campos["port"] = campos["port"] or 5432
    campos["dbname"] = campos["dbname"] or "postgres"
    if not all(campos[name] for name in ("host", "user", "password")):
        raise ConfigurationError("Configure a conexão com o Supabase para começar.")
    try:
        campos["port"] = int(campos["port"])
    except (ValueError, TypeError):
        raise ConfigurationError("A porta do banco deve ser um número válido.") from None
    return ServicoFinanceiro(RepositorioPostgres(DatabaseConfig(**campos)))
