import hashlib
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

BASE_DIR = Path(__file__).parent.parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

CAIXABANK_SHEET_ID = "154ovBGpaMOwoLAKN0wVHc12Ebr72t9LtzjHhjvy-oeM"
SANTANDER_SHEET_ID = "1KfGcbeJYaoxJHfAwZuqEHflYcZsX1zfnUVowopS9cPk"


def _get_client() -> gspread.Client:
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            "No se encontró token.json. Ejecuta 'python auth.py' primero para autenticarte con Google."
        )

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())

    return gspread.authorize(creds)


def _parse_date(raw: str) -> date | None:
    if not raw or not raw.strip():
        return None
    s = raw.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_amount(raw: str) -> float | None:
    if not raw or not raw.strip():
        return None
    s = raw.strip().replace("\xa0", "").replace(" ", "")
    # European format: 1.234,56 → 1234.56
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _dedup_hash(account: str, d: date, amount: float, description: str) -> str:
    content = f"{account}|{d}|{amount:.2f}|{description[:80]}"
    return hashlib.md5(content.encode()).hexdigest()


def import_caixabank() -> list[dict[str, Any]]:
    """
    CaixaBank columns:
    Fecha | Fecha valor | Movimiento | Más datos | Importe | Saldo | CONCEPTO
    """
    gc = _get_client()
    rows = gc.open_by_key(CAIXABANK_SHEET_ID).sheet1.get_all_values()
    if not rows:
        return []

    header_idx = next(
        (i for i, r in enumerate(rows) if any("fecha" in c.lower() for c in r)),
        0,
    )
    results = []
    for row in rows[header_idx + 1 :]:
        if len(row) < 5 or not row[0].strip():
            continue

        fecha = _parse_date(row[0])
        fecha_valor = _parse_date(row[1]) if len(row) > 1 else None
        movimiento = row[2].strip() if len(row) > 2 else ""
        mas_datos = row[3].strip() if len(row) > 3 else ""
        importe = _parse_amount(row[4]) if len(row) > 4 else None
        saldo = _parse_amount(row[5]) if len(row) > 5 else None
        concepto = row[6].strip() if len(row) > 6 else ""

        if fecha is None or importe is None:
            continue

        description = movimiento or mas_datos or "Sin descripción"
        results.append(
            {
                "account_code": "caixabank",
                "date": fecha,
                "value_date": fecha_valor,
                "description": description,
                "concepto": concepto,
                "amount": importe,
                "balance_after": saldo,
                "dedup_hash": _dedup_hash("caixabank", fecha, importe, description),
            }
        )
    return results


def import_santander() -> list[dict[str, Any]]:
    """
    Santander columns:
    FECHA OPERACIÓN | FECHA VALOR | CONCEPTO banco | IMPORTE EUR | SALDO | CONCEPTO etiqueta
    """
    gc = _get_client()
    rows = gc.open_by_key(SANTANDER_SHEET_ID).sheet1.get_all_values()
    if not rows:
        return []

    header_idx = next(
        (i for i, r in enumerate(rows) if any("fecha" in c.lower() for c in r)),
        0,
    )
    results = []
    for row in rows[header_idx + 1 :]:
        if len(row) < 4 or not row[0].strip():
            continue

        fecha = _parse_date(row[0])
        fecha_valor = _parse_date(row[1]) if len(row) > 1 else None
        concepto_banco = row[2].strip() if len(row) > 2 else ""
        importe = _parse_amount(row[3]) if len(row) > 3 else None
        saldo = _parse_amount(row[4]) if len(row) > 4 else None
        concepto_etiqueta = row[5].strip() if len(row) > 5 else ""

        if fecha is None or importe is None:
            continue

        results.append(
            {
                "account_code": "santander",
                "date": fecha,
                "value_date": fecha_valor,
                "description": concepto_banco,
                "concepto": concepto_etiqueta,
                "amount": importe,
                "balance_after": saldo,
                "dedup_hash": _dedup_hash("santander", fecha, importe, concepto_banco),
            }
        )
    return results
