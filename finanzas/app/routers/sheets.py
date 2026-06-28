import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..categories import map_category
from ..database import get_db
from ..models import Account, Movement
from ..services.google_sheets import import_caixabank, import_santander

router = APIRouter()


def _get_or_create_account(db: Session, code: str, name: str) -> Account:
    acc = db.query(Account).filter(Account.code == code).first()
    if not acc:
        acc = Account(code=code, name=name)
        db.add(acc)
        db.commit()
        db.refresh(acc)
    return acc


def _import_account(db: Session, acc: Account, raw_movements: list, batch_id: str) -> dict:
    imported = skipped = 0
    last_balance = None

    for m in raw_movements:
        if db.query(Movement).filter(Movement.dedup_hash == m["dedup_hash"]).first():
            skipped += 1
            continue

        category = map_category(m["concepto"], m["amount"])
        db.add(
            Movement(
                account_id=acc.id,
                date=m["date"],
                value_date=m["value_date"],
                description=m["description"],
                concepto=m["concepto"],
                category=category,
                amount=m["amount"],
                balance_after=m["balance_after"],
                is_manual=False,
                dedup_hash=m["dedup_hash"],
                import_batch=batch_id,
            )
        )
        imported += 1
        if m["balance_after"] is not None:
            last_balance = m["balance_after"]

    if last_balance is not None:
        acc.balance = last_balance
        acc.last_updated = datetime.utcnow()

    db.commit()
    return {"imported": imported, "skipped": skipped}


@router.post("/sheets")
def import_sheets(db: Session = Depends(get_db)):
    batch_id = str(uuid.uuid4())[:8]
    results: dict = {"batch": batch_id, "caixabank": {}, "santander": {}, "errors": []}

    try:
        acc = _get_or_create_account(db, "caixabank", "CaixaBank")
        results["caixabank"] = _import_account(db, acc, import_caixabank(), batch_id)
    except Exception as e:
        results["errors"].append(f"CaixaBank: {e}")

    try:
        acc = _get_or_create_account(db, "santander", "Santander")
        results["santander"] = _import_account(db, acc, import_santander(), batch_id)
    except Exception as e:
        results["errors"].append(f"Santander: {e}")

    return results


@router.get("/status")
def auth_status():
    from pathlib import Path
    token = Path(__file__).parent.parent.parent / "token.json"
    creds = Path(__file__).parent.parent.parent / "credentials.json"
    return {
        "token_exists": token.exists(),
        "credentials_exists": creds.exists(),
        "ready": token.exists(),
    }
