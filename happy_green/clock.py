"""A data financeira segue Brasília também quando a hospedagem usa UTC."""

from datetime import date, datetime
from zoneinfo import ZoneInfo


def hoje() -> date:
    return datetime.now(ZoneInfo("America/Sao_Paulo")).date()
