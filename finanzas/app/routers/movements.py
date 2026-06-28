import calendar
import hashlib
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..categories import ALL_CATEGORIES, EXTRA_PAY_MONTHS, map_category
from ..database import get_db
from ..models import Account, Movement

router = APIRouter()


class MovementCreate(BaseModel):
    account_code: str = "revolut"
    date: date
    description: str
    concepto: Optional[str] = None
    amount: float
    notes: Optional[str] = None


def _serialize(m: Movement) -> dict:
    return {
        "id": m.id,
        "account_code": m.account.code,
        "account_name": m.account.name,
        "date": m.date.isoformat(),
        "description": m.description,
        "concepto": m.concepto,
        "category": m.category,
        "amount": m.amount,
        "balance_after": m.balance_after,
        "notes": m.notes,
        "is_manual": m.is_manual,
    }


@router.get("/")
def list_movements(
    year: Optional[int] = None,
    month: Optional[int] = None,
    account: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Movement).join(Account)

    if year and month:
        last_day = calendar.monthrange(year, month)[1]
        q = q.filter(
            Movement.date >= date(year, month, 1),
            Movement.date <= date(year, month, last_day),
        )
    elif year:
        q = q.filter(
            Movement.date >= date(year, 1, 1),
            Movement.date <= date(year, 12, 31),
        )

    if account:
        q = q.filter(Account.code == account)
    if category:
        q = q.filter(Movement.category == category)

    return [_serialize(m) for m in q.order_by(Movement.date.desc()).all()]


@router.post("/")
def create_movement(body: MovementCreate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.code == body.account_code).first()
    if not account:
        account = Account(code=body.account_code, name=body.account_code.capitalize())
        db.add(account)
        db.commit()
        db.refresh(account)

    category = map_category(body.concepto or "", body.amount)
    dedup = hashlib.md5(
        f"manual|{body.date}|{body.amount:.2f}|{body.description}|{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()

    m = Movement(
        account_id=account.id,
        date=body.date,
        description=body.description,
        concepto=body.concepto,
        category=category,
        amount=body.amount,
        notes=body.notes,
        is_manual=True,
        dedup_hash=dedup,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"id": m.id, "category": m.category}


@router.patch("/{movement_id}/category")
def update_category(
    movement_id: int,
    category: str = Query(...),
    db: Session = Depends(get_db),
):
    m = db.query(Movement).filter(Movement.id == movement_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    if category not in ALL_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Categoría inválida: {category}")
    m.category = category
    db.commit()
    return {"ok": True}


@router.delete("/{movement_id}")
def delete_movement(movement_id: int, db: Session = Depends(get_db)):
    m = db.query(Movement).filter(Movement.id == movement_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    db.delete(m)
    db.commit()
    return {"ok": True}


@router.get("/summary/{year}/{month}")
def monthly_summary(year: int, month: int, db: Session = Depends(get_db)):
    last_day = calendar.monthrange(year, month)[1]
    movements = (
        db.query(Movement)
        .filter(
            Movement.date >= date(year, month, 1),
            Movement.date <= date(year, month, last_day),
        )
        .all()
    )

    by_category: dict[str, dict] = {}
    total_income = 0.0
    total_expenses = 0.0

    for m in movements:
        cat = m.category
        if cat not in by_category:
            by_category[cat] = {"income": 0.0, "expenses": 0.0, "count": 0}
        if m.amount >= 0:
            by_category[cat]["income"] += m.amount
            total_income += m.amount
        else:
            by_category[cat]["expenses"] += abs(m.amount)
            total_expenses += abs(m.amount)
        by_category[cat]["count"] += 1

    return {
        "year": year,
        "month": month,
        "is_extra_pay_month": month in EXTRA_PAY_MONTHS,
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "balance": round(total_income - total_expenses, 2),
        "by_category": by_category,
    }


@router.get("/tennis/{year}/{month}")
def tennis_summary(year: int, month: int, db: Session = Depends(get_db)):
    """Desglose detallado de los gastos de Tenis Lucía."""
    last_day = calendar.monthrange(year, month)[1]
    movements = (
        db.query(Movement)
        .filter(
            Movement.date >= date(year, month, 1),
            Movement.date <= date(year, month, last_day),
            Movement.category == "Tenis Lucía",
        )
        .all()
    )

    # Annual totals
    annual = (
        db.query(Movement)
        .filter(
            Movement.date >= date(year, 1, 1),
            Movement.date <= date(year, 12, 31),
            Movement.category == "Tenis Lucía",
        )
        .all()
    )

    by_concept: dict[str, float] = {}
    for m in movements:
        key = m.concepto or m.description
        by_concept[key] = by_concept.get(key, 0.0) + abs(m.amount)

    return {
        "year": year,
        "month": month,
        "monthly_total": round(sum(abs(m.amount) for m in movements), 2),
        "annual_total": round(sum(abs(m.amount) for m in annual), 2),
        "by_concept": by_concept,
        "movements": [_serialize(m) for m in movements],
    }
